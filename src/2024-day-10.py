import typing
import sys
import uuid
import logging
from dataclasses import dataclass, field


logging.basicConfig(level=logging.WARNING, handlers=[logging.StreamHandler(sys.stdout)])


log = logging.getLogger(__name__)


FilePath: typing.TypeAlias = str
StreamOfChars: typing.TypeAlias = typing.Iterator[str]


class OpenStream(typing.Protocol):
    def __call__(self, file: FilePath) -> StreamOfChars: ...


def stream_opener(file: FilePath) -> StreamOfChars:
    with open(file) as file_handler:
        while character := file_handler.read(1):
            yield character


read_char: OpenStream = stream_opener


@dataclass
class Point:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    lat: int = 0
    long: int = 0
    height: int = 0
    trailhead: bool = False
    peaks: list["Point"] = field(default_factory=list)
    trails: list["Trail"] = field(default_factory=list)

    def add_peak(self, peak: "Point"):
        if self.trailhead is False:
            self.trailhead = True
        if peak not in self.peaks:
            self.peaks.append(peak)

    def add_trail(self, trail: "Trail"):
        if self.trailhead is False:
            self.trailhead = True
        if trail not in self.trails:
            self.trails.append(trail)


@dataclass
class Row:
    points: list[Point] = field(default_factory=list)

    def add_point(self, point: Point):
        self.points.append(point)


@dataclass
class Map:
    rows: list[Row] = field(default_factory=list)
    trails: list["Trail"] = field(default_factory=list)
    point_getters: list[typing.Callable] = field(default_factory=list)

    def __post_init__(self):
        self.point_getters += [self.get_point_up, self.get_point_right, self.get_point_down, self.get_point_left]

    def load_points(self, file_opener: OpenStream, file_path: str):
        row = Row()
        for character in file_opener(file_path):
            if character == "\n":
                self.add_row(row)
                row = Row()
                continue
            if character == ".":
                row.add_point(Point(lat=len(self.rows), long=len(row.points), height=-1))
                continue
            height = int(character)
            row.add_point(Point(lat=len(self.rows), long=len(row.points), height=height))

    def count_trailheads(self) -> list[Point]:
        trailheads: list[Point] = []
        for row in self.rows:
            for point in row.points:
                if point.trailhead is True:
                    trailheads.append(point)
        return trailheads

    def count_score(self) -> int:
        score = 0
        for row in self.rows:
            for point in row.points:
                if point.trailhead is True:
                    score += len(point.peaks)
        return score

    def count_rating(self) -> int:
        rating = 0
        for row in self.rows:
            for point in row.points:
                if point.trailhead is True:
                    rating += len(point.trails)
        return rating

    def add_row(self, row: Row):
        self.rows.append(row)

    def add_trail(self, trail: "Trail"):
        self.trails.append(trail)

    def get_point_up(self, point: Point) -> Point:
        col = point.long
        row = point.lat - 1
        if row < 0:
            raise ValueError("Asked point up from: ", point, ", is out of the map")
        return self.rows[row].points[col]

    def get_point_down(self, point: Point) -> Point:
        col = point.long
        row = point.lat + 1
        if row > len(self.rows) - 1:
            raise ValueError("Asked point down from: ", point, ", is out of the map")
        return self.rows[row].points[col]

    def get_point_left(self, point: Point) -> Point:
        col = point.long - 1
        row = point.lat
        if col < 0:
            raise ValueError("Asked point left from: ", point, ", is out of the map")
        return self.rows[row].points[col]

    def get_point_right(self, point: Point) -> Point:
        col = point.long + 1
        row = point.lat
        if col > len(self.rows[row].points) - 1:
            raise ValueError("Asked point right from: ", point, ", is out of the map")
        return self.rows[row].points[col]

    def try_new_trail(self, trailhead: Point, point_getter: typing.Callable):
        trail: Trail = Trail()
        try:
            point: Point = point_getter(trailhead)
            trail.add_point(trailhead)
            trail.add_point(point)
        except ValueError:
            log.info(f"Cannot add new trail for trailhead: {trailhead.id}.")
        else:
            self.add_trail(trail)

    def find_new_trails(self):
        for row, instance in enumerate(self.rows):
            for col, _ in enumerate(instance.points):
                point: Point = self.rows[row].points[col]
                for point_getter in self.point_getters:
                    if point.height == 0:
                        self.try_new_trail(point, point_getter)

    def find_not_processed_trails(self):
        return [trail for trail in self.trails if trail.processed is False]

    def finish_trails(self):
        while trails := self.find_not_processed_trails():
            for trail in trails:
                trail.find_way(self)


@dataclass
class Trail:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    path: list[Point] = field(default_factory=list)
    processed: bool = False

    def next_point(self, trail_map: Map, point: Point) -> Point | None:  # noqa[C901] (6)
        next_points: list[Point] = []
        for point_getter in trail_map.point_getters:
            try:
                next_point: Point = point_getter(point)
                self.__validate_point(next_point)
                next_points.append(next_point)
                if len(next_points) > 1:
                    new_trail: Trail = Trail(path=list(self.path))
                    new_trail.add_point(next_point)
                    trail_map.add_trail(new_trail)
            except ValueError:
                log.info("Cannot find next point.")
        if next_points:
            return next_points[0]
        return None

    def find_way(self, trail_map: Map):
        if self.processed is False:
            self.processed = True
        last_point: Point = self.path[-1]
        try:
            while next_point := self.next_point(trail_map, last_point):
                self.add_point(next_point)
                last_point = next_point
        except ValueError:
            log.info(f"Finding way is over, last point is {last_point.id}.")

    def add_point(self, point: Point):
        self.__validate_point(point)
        self.path.append(point)
        self.__post_add_point(point)

    def __validate_point(self, point):
        if len(self.path) > 0:
            last_point = self.path[-1]
            if abs(last_point.lat - point.lat) + abs(last_point.long - point.long) > 1:
                raise ValueError("Point: ", point, ", is not near to: ", last_point)
            if point.height - last_point.height != 1:
                raise ValueError("Point: ", point, ", does not fit in the path: ", self.path)
        else:
            if point.height != 0:
                raise ValueError("Point: ", point, ", cannot be start of the trail")

    def __post_add_point(self, point):
        if point.height == 9:
            trailhead: Point = self.path[0]
            trailhead.add_peak(point)
            trailhead.add_trail(self)


if __name__ == "__main__":
    from rich import print

    file_path: FilePath = "../media/2024-day-10.input"

    trail_map = Map()
    trail_map.load_points(read_char, file_path)
    trail_map.find_new_trails()
    trail_map.finish_trails()

    print(open(file_path).read())
    print("Score: ", trail_map.count_score())
    print("Rating: ", trail_map.count_rating())
