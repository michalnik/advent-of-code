import argparse
import typing
from functools import reduce

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    create_stream_of_lines,
    StreamOfLines,
    FilePath,
)


CountOfPositions: typing.TypeAlias = int
Grid: typing.TypeAlias = list[list[str]]
Coords: typing.TypeAlias = tuple[int, int]
Direction: typing.TypeAlias = str
Directions: typing.TypeAlias = list[str]


POSSIBLE_DIRECTIONS: Directions = ["N", "E", "S", "W"]


class Rules(typing.Protocol):
    def __call__(self, grid: Grid, current_coords: Coords, direction: Direction) -> tuple[Coords, Direction]: ...


class PredictGuardMovements(typing.Protocol):
    def __call__(self, stream: typing.Iterator[StreamOfLines], rules: Rules) -> typing.Iterator[StreamOfLines]: ...


class AddUpCountOfDistinctPositionsInThePath(typing.Protocol):
    def __call__(self, stream: typing.Iterator[StreamOfLines]) -> CountOfPositions: ...


def load_grid(stream: StreamOfLines) -> Grid:
    return list([letter for letter in line.strip()] for line in stream)


def find_letter_in_line(row_idx: int, row: list[str], letter: str = "^") -> Coords | None:
    for col_idx, _letter in enumerate(row):
        if letter == _letter:
            return row_idx, col_idx
    return None


def find_letter(grid: Grid, letter: str = "^", mark_pos: bool = True) -> Coords | None:
    coords: Coords | None
    for idx, line in enumerate(grid):
        if coords := find_letter_in_line(idx, line, letter):
            if mark_pos is True:
                grid[coords[0]][coords[1]] = "X"
            return coords
    return None


def apply_rules(grid: Grid, start_coords: Coords, rules: Rules):
    direction: Direction = "N"
    current_coords: Coords = start_coords
    while True:
        try:
            current_coords, direction = rules(grid, current_coords, direction)
        except ValueError:
            # being at the end of the path
            break


def store_grid(grid: Grid, tmp_file: FilePath):
    with open(tmp_file, "w") as file_handler:
        for row in grid:
            for col in row:
                file_handler.write(col)


def predict_guard_movements_by_default(
    stream: typing.Iterator[StreamOfLines], rules: Rules
) -> typing.Iterator[StreamOfLines]:
    tmp_file: FilePath = "/tmp/advent-of-code-data.tmp"
    grid: Grid = load_grid(next(stream))
    start_coords: Coords | None = find_letter(grid)
    if start_coords:
        apply_rules(grid, start_coords, rules)
    store_grid(grid, tmp_file)
    return create_stream_of_lines(tmp_file)


def adding_up_distinct_positions_for_line(line: str) -> CountOfPositions:
    return reduce(lambda accumulator, letter: accumulator + 1 if letter == "X" else accumulator, line, 0)


def adding_up_distinct_positions_by_default(stream: typing.Iterator[StreamOfLines]) -> CountOfPositions:
    return reduce(lambda accumulator, line: accumulator + adding_up_distinct_positions_for_line(line), next(stream), 0)


def get_next_coords(current_coords: Coords, direction: Direction) -> Coords:
    next_coords: Coords
    match direction:
        case "N":
            next_coords = current_coords[0] - 1, current_coords[1]
        case "S":
            next_coords = current_coords[0] + 1, current_coords[1]
        case "E":
            next_coords = current_coords[0], current_coords[1] + 1
        case _:
            next_coords = current_coords[0], current_coords[1] - 1
    return next_coords


def get_next_direction(direction: Direction) -> Direction:
    try:
        return POSSIBLE_DIRECTIONS[POSSIBLE_DIRECTIONS.index(direction) + 1]
    except IndexError:
        return POSSIBLE_DIRECTIONS[0]


def default_rules(grid: Grid, current_coords: Coords, direction: Direction) -> tuple[Coords, Direction]:
    next_coords = get_next_coords(current_coords, direction)
    try:
        if next_coords[0] < 0 or next_coords[1] < 0:
            raise IndexError
        match grid[next_coords[0]][next_coords[1]]:
            case "#":
                direction = get_next_direction(direction)
            case _:
                current_coords = next_coords
    except IndexError:
        raise ValueError("The end of the path")
    else:
        # mark the going through path
        grid[current_coords[0]][current_coords[1]] = "X"
    return current_coords, direction


def main(args: argparse.Namespace):
    count_of_positions: CountOfPositions
    stream: typing.Iterator[StreamOfLines] = create_stream_of_lines(args.file_path)

    rules: Rules
    match args.mode:
        case _:
            rules = default_rules

    predict_guard_movements: PredictGuardMovements
    match args.mode:
        case _:
            predict_guard_movements = predict_guard_movements_by_default

    stream = predict_guard_movements(stream, rules)

    adding_up_distinct_positions: AddUpCountOfDistinctPositionsInThePath
    match args.mode:
        case _:
            adding_up_distinct_positions = adding_up_distinct_positions_by_default

    count_of_positions = adding_up_distinct_positions(stream)

    print(f"Added up distinct positions of the guard in the path by mode <{args.mode}>: ", count_of_positions)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        (
            "Go through input data array (2 dimensional):\n\n"
            "\t1) apply the rules for guard movement\n"
            "\t2) mark the resulting path in the array.\n\n"
            "Add up the summary of distinct positions on the guard path.\n"
        )
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["default"],
        default="default",
        help="Mode of solving these problems",
    )

    parse_args_run_and_profile(parser, main)
