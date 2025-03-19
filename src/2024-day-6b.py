import argparse
import typing

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    create_stream_of_lines,
    StreamOfLines,
)


CountOfPositions: typing.TypeAlias = int
Grid: typing.TypeAlias = list[list[str]]
Coords: typing.TypeAlias = tuple[int, int]
Direction: typing.TypeAlias = typing.Literal["N", "E", "S", "W"]
Directions: typing.TypeAlias = list[Direction]


POSSIBLE_DIRECTIONS: Directions = list(typing.get_args(Direction))
VISUALIZE_TIME_LOOP: dict[str, str] = {"N": "^", "S": "v", "W": "<", "E": ">"}


class Rules(typing.Protocol):
    def __call__(
        self, grid: Grid, coords: Coords, direction: Direction, count_of_new_blocks: CountOfPositions
    ) -> tuple[Coords, Direction, CountOfPositions]: ...


class PredictGuardMovements(typing.Protocol):
    def __call__(self, stream: typing.Iterator[StreamOfLines], rules: Rules) -> CountOfPositions: ...


def validate_coords(grid: Grid, coords: Coords):
    if coords[0] < 0:
        raise ValueError(f"Upper edge of grid exceeded at {coords}s.")
    if coords[1] < 0:
        raise ValueError(f"Left edge of grid exceeded at {coords}s.")
    if len(grid) - 1 < coords[0]:
        raise ValueError(f"Lower edge of grid exceeded at {coords}s.")
    if len(grid[0]) - 1 < coords[1]:
        raise ValueError(f"Right edge of grid exceeded at {coords}s.")


def get_next_coords(grid: Grid, current_coords: Coords, direction: Direction) -> Coords:
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
    validate_coords(grid, next_coords)
    return next_coords


def get_next_direction(direction: Direction, next_letter: str) -> Direction:
    if next_letter != "#":
        return direction
    try:
        return POSSIBLE_DIRECTIONS[POSSIBLE_DIRECTIONS.index(direction) + 1]
    except IndexError:
        return POSSIBLE_DIRECTIONS[0]


def get_mark_of_path(direction: Direction, next_letter: str) -> str:
    mark_of_path: str
    match next_letter:
        case "#":
            mark_of_path = "+"
        case "-":
            mark_of_path = "+" if direction in ["N", "S"] else "-"
        case "|":
            mark_of_path = "+" if direction in ["E", "W"] else "|"
        case "^":
            mark_of_path = "^"
        case _:
            mark_of_path = "-" if direction in ["E", "W"] else "|"
    return mark_of_path


def get_next_guard_step(current_coords: Coords, next_coords: Coords, next_letter: str) -> Coords:
    match next_letter:
        case "#":
            return current_coords
        case _:
            return next_coords


def stuck_in_loop(search_area: Grid, coords: Coords, direction: Direction) -> bool:
    if search_area[coords[0]][coords[1]] == VISUALIZE_TIME_LOOP[direction]:
        # meet time loop path again
        return True
    return False


def found_time_loop(grid: Grid, coords: Coords, direction: Direction) -> bool:  # noqa: [C901]
    search_area: Grid = [[letter for letter in line] for line in grid]
    next_coords: Coords
    loop_counter: int = 0
    while True:
        loop_counter += 1
        if loop_counter > 7500:
            print(f"Found complex time loop at {coords}")
            return True
        try:
            next_coords = get_next_coords(search_area, coords, direction)
        except ValueError as exc:
            print(f"Searching time loop ends up out of grid: {exc}")
            # out of grid: there is no possibility to return back
            return False
        match search_area[next_coords[0]][next_coords[1]]:
            case "#":
                direction = get_next_direction(direction, "#")
            case _:
                coords = next_coords
        if stuck_in_loop(search_area, coords, direction):
            print(f"Found simple time loop at {coords}")
            return True
        else:
            # record move to find loop
            search_area[coords[0]][coords[1]] = VISUALIZE_TIME_LOOP[direction]
            continue


def default_rules(
    grid: Grid, coords: Coords, direction: Direction, count_of_new_blocks: CountOfPositions
) -> tuple[Coords, Direction, CountOfPositions]:
    probably_next_coords: Coords = get_next_coords(grid, coords, direction)
    next_letter: str = grid[probably_next_coords[0]][probably_next_coords[1]]
    next_direction: Direction = get_next_direction(direction, next_letter)
    next_guard_step: Coords = get_next_guard_step(coords, probably_next_coords, next_letter)
    mark_of_path: str = get_mark_of_path(next_direction, next_letter)
    if next_letter not in ["#", "^", "+", "|", "-"]:
        # place single obstacle
        grid[probably_next_coords[0]][probably_next_coords[1]] = "#"
        if found_time_loop(grid, coords, get_next_direction(direction, "#")):
            count_of_new_blocks += 1
        # restore original letter
        grid[probably_next_coords[0]][probably_next_coords[1]] = next_letter
    # mark the path
    grid[next_guard_step[0]][next_guard_step[1]] = mark_of_path
    return next_guard_step, next_direction, count_of_new_blocks


def load_grid(stream: StreamOfLines) -> Grid:
    return list([letter for letter in line.strip()] for line in stream)


def find_letter_in_line(row_idx: int, row: list[str], letter: str = "^") -> Coords | None:
    for col_idx, _letter in enumerate(row):
        if letter == _letter:
            return row_idx, col_idx
    return None


def find_letter(grid: Grid, letter: str = "^") -> Coords | None:
    coords: Coords | None
    for idx, line in enumerate(grid):
        if coords := find_letter_in_line(idx, line, letter):
            return coords
    return None


def apply_rules(grid: Grid, start_coords: Coords, rules: Rules) -> CountOfPositions:
    count_of_new_blocks: CountOfPositions = 0
    next_direction: Direction = "N"
    next_coords: Coords = start_coords
    while True:
        try:
            next_coords, next_direction, count_of_new_blocks = rules(
                grid, next_coords, next_direction, count_of_new_blocks
            )
        except ValueError as exc:
            print("End of the guard path:", exc)
            break
    return count_of_new_blocks


def predict_movement_and_count_blocks_by_default(
    stream: typing.Iterator[StreamOfLines], rules: Rules
) -> CountOfPositions:
    count_of_new_blocks: CountOfPositions = 0
    grid: Grid = load_grid(next(stream))
    start_coords: Coords | None = find_letter(grid)
    if start_coords:
        count_of_new_blocks = apply_rules(grid, start_coords, rules)
    return count_of_new_blocks


def main(args: argparse.Namespace):
    stream: typing.Iterator[StreamOfLines] = create_stream_of_lines(args.file_path)

    rules: Rules
    match args.mode:
        case _:
            rules = default_rules

    predict_guard_movements: PredictGuardMovements
    match args.mode:
        case _:
            predict_guard_movements = predict_movement_and_count_blocks_by_default

    count_new_blocks: CountOfPositions = predict_guard_movements(stream, rules)

    print(f"Added up blocks of the guard in the path by mode <{args.mode}>: ", count_new_blocks)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        (
            "Go through input data array (2 dimensional):\n\n"
            "\t1) apply the rules for guard movement\n"
            "\t2) mark the resulting path in the array.\n\n"
            "Add up possible blocks for guard movements on the guard path.\n"
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
