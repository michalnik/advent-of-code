import argparse
import typing

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    create_stream_of_lines,
    StreamOfLines,
)


COUNT_OF_POSITIONS: typing.TypeAlias = int


class AddUpCountOfDistinctPositionsInThePath(typing.Protocol):
    def __call__(self, stream: typing.Iterator[StreamOfLines]) -> COUNT_OF_POSITIONS: ...


def adding_up_distinct_positions(stream: typing.Iterator[StreamOfLines]) -> COUNT_OF_POSITIONS:
    return 0


def main(args: argparse.Namespace):
    count_of_positions: COUNT_OF_POSITIONS

    adding_up_middle_page_numbers: AddUpCountOfDistinctPositionsInThePath
    match args.mode:
        case _:
            adding_up_middle_page_numbers = adding_up_distinct_positions

    count_of_positions = adding_up_middle_page_numbers(create_stream_of_lines(args.file_path))

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
