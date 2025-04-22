#!/usr/bin/env python
# coding: utf-8
import typing
from rich import print
import uuid
from dataclasses import dataclass, field


FilePath: typing.TypeAlias = str
FileContent: typing.TypeAlias = list[str]


class FileReader(typing.Protocol):
    def __call__(self, file: FilePath) -> FileContent: ...


def file_reader(file: FilePath) -> FileContent:
    with open(file) as file_handler:
        return [line for line in file_handler.read().splitlines(keepends=False) if len(line) > 0]


data_reader: FileReader = file_reader


@dataclass(frozen=True)
class Plot:
    x: int
    y: int
    plant_type: str


@dataclass
class Region:
    _id: uuid.UUID = field(init=False)
    plots: list[Plot] = field(default_factory=list)
    area: int | None = None
    perimeter: int | None = None
    price: int | None = None

    def __post_init__(self):
        self._id = uuid.uuid4()

    def calculate_area(self) -> int:
        self.area = len(self.plots)
        return self.area

    def calculate_price(self) -> int:
        if self.perimeter is None:
            raise ValueError("Perimeter is missing for region: ", self._id)
        area: int = self.calculate_area()
        self.price = area * self.perimeter
        return self.price


@dataclass
class Regions:
    regions: list[Region]

    def calculate_price(self) -> int:
        price: int = 0
        for region in self.regions:
            price += region.calculate_price()
        return price


@dataclass
class Grid:
    content: FileContent = field(default_factory=list)
    data: list[list[Plot | None]] = field(default_factory=list)

    def load_from_file(self, file_content: FileContent):
        self.content = file_content
        self.data = []
        for y, line in enumerate(file_content):
            for x, character in enumerate(line):
                if x == 0:
                    self.data.append([Plot(x=x, y=y, plant_type=character)])
                else:
                    self.data[y].append(Plot(x=x, y=y, plant_type=character))

    def get_point(self, x: int, y: int) -> Plot | None:
        return self.data[y][x]

    @staticmethod
    def region_filter(plot: Plot, neighbour: Plot | None, region: bool = True) -> Plot | None:
        if region and neighbour:
            if neighbour.plant_type != plot.plant_type:
                return None
        return neighbour

    def get_neighbours(self, plot: Plot | None, region: bool = False) -> list[Plot | None]:  # noqa[C901] (8)
        if plot is None:
            return []

        left, right, up, down = None, None, None, None
        if plot.x > 0:
            left = self.region_filter(plot, self.data[plot.y][plot.x - 1], region)
        if plot.x < len(self.data[plot.y]) - 1:
            right = self.region_filter(plot, self.data[plot.y][plot.x + 1], region)
        if plot.y > 0:
            up = self.region_filter(plot, self.data[plot.y - 1][plot.x], region)
        if plot.y < len(self.data) - 1:
            down = self.region_filter(plot, self.data[plot.y + 1][plot.x], region)
        neighbours: list[Plot | None] = [left, right, up, down]
        return neighbours

    def get_region_neighbours(self, plot: Plot | None) -> set[Plot]:
        neighbours: list[Plot | None] = self.get_neighbours(plot, True)
        return set(p for p in neighbours if p is not None)

    def get_perimeter(self, plot: Plot) -> int:
        neighbours: list[Plot | None] = self.get_neighbours(plot)
        perimeter: int = 0
        for neighbour in neighbours:
            if neighbour is None or neighbour.plant_type != plot.plant_type:
                perimeter += 1
        return perimeter

    def calculate_perimeter(self, regions: Regions) -> int:
        perimeter: int = 0
        for region in regions.regions:
            _perimeter: int = 0
            for point in region.plots:
                _perimeter += self.get_perimeter(point)
            region.perimeter = _perimeter
            perimeter += _perimeter
        return perimeter

    def __reload_from_regions(self, regions: Regions):
        for region in regions.regions:
            for plot in region.plots:
                self.data[plot.y][plot.x] = plot

    def reveal_regions(self) -> Regions:  # noqa[C901] (6)
        _regions: Regions = Regions(regions=[])
        for y, plots in enumerate(self.data):
            for x, plot in enumerate(plots):
                if plot is None:
                    continue
                neighbours: set[Plot] = set()
                _neighbours: set[Plot] = {plot}
                while _neighbours:
                    _next: set[Plot] = set()
                    for neighbour in _neighbours:
                        self.data[neighbour.y][neighbour.x] = None
                        _next.update(self.get_region_neighbours(neighbour))
                    neighbours.update(_neighbours)
                    _neighbours = _next
                _regions.regions.append(Region(plots=list(neighbours)))
        self.__reload_from_regions(_regions)
        return _regions


if __name__ == "__main__":
    garden_plots: FileContent = data_reader("../media/2024-day-12.input")
    grid: Grid = Grid()
    grid.load_from_file(garden_plots)
    regs: Regions = grid.reveal_regions()
    print("Grid perimeter: ", grid.calculate_perimeter(regs))
    print("Regions price: ", regs.calculate_price())
