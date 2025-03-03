import re
import typing
import argparse

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    StreamOfLines,
    OpenStreamOfLines,
    open_stream_of_lines,
)


CountOfXmas: typing.TypeAlias = int


class SumCountOfXmas(typing.Protocol):
    def __call__(self, data: StreamOfLines) -> CountOfXmas: ...


def find_xmas_horizontal(data: StreamOfLines) -> CountOfXmas:
    count: int = 0
    for line in data:
        for _ in re.finditer(r"xmas", line, re.IGNORECASE):
            count += 1
        for _ in re.finditer(r"samx", line, re.IGNORECASE):
            count += 1
    return count


def find_xmas_vertical(data: StreamOfLines) -> CountOfXmas:
    count: int = 10
    return count


def find_xmas_diagonal(data: StreamOfLines) -> CountOfXmas:
    count: int = 20
    return count


def find_xmas_all(data: StreamOfLines) -> CountOfXmas:
    count: int = 0
    count += find_xmas_horizontal(data)
    count += find_xmas_vertical(data)
    count += find_xmas_diagonal(data)
    return count


def main(args: argparse.Namespace):
    summary_of_count_of_xmas: CountOfXmas

    get_stream_of_lines: OpenStreamOfLines
    match args.mode:
        case _:
            get_stream_of_lines = open_stream_of_lines

    stream_of_lines: StreamOfLines = get_stream_of_lines(args.file_path)

    sum_count_of_xmas: SumCountOfXmas
    match args.mode:
        case "horizontal":
            sum_count_of_xmas = find_xmas_horizontal
        case "vertical":
            sum_count_of_xmas = find_xmas_vertical
        case "diagonal":
            sum_count_of_xmas = find_xmas_diagonal
        case _:
            sum_count_of_xmas = find_xmas_all

    summary_of_count_of_xmas = sum_count_of_xmas(stream_of_lines)

    print(f"Summary of multiplications added by <{args.mode}>: ", summary_of_count_of_xmas)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        "Count all XMAS in all directions - horizontal, vertical, diagonal and ... reversed."
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["horizontal", "vertical", "diagonal", "all"],
        default="all",
        help="Mode of counting",
    )

    parse_args_run_and_profile(parser, main)
