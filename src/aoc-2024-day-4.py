import re
import typing
import argparse

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    StreamOfLines,
    create_stream_of_lines,
)


CountOfXmas: typing.TypeAlias = int
SearchBlock: typing.TypeAlias = list[str]
SearchPattern: typing.TypeAlias = list[tuple[int, str]]


class SumCountOfXmas(typing.Protocol):
    def __call__(self, data: typing.Iterator[StreamOfLines]) -> CountOfXmas: ...


def find_xmas_horizontal(data: StreamOfLines) -> CountOfXmas:
    count: int = 0
    for line in data:
        for _ in re.finditer(r"xmas", line, re.IGNORECASE):
            count += 1
        for _ in re.finditer(r"samx", line, re.IGNORECASE):
            count += 1
    return count


def is_interesting_block(block_idx: int, line_idx: int) -> bool:
    return block_idx <= line_idx


def search_block_vertical(search_block: SearchBlock, pattern: SearchPattern) -> CountOfXmas:
    count_of_xmas: int = 0
    try:
        for col_idx in range(len(search_block[0])):
            if all(
                search_block[row_idx][col_idx + search[0]].lower() == search[1]
                for row_idx, search in zip(list(range(4)), pattern)
            ):
                count_of_xmas += 1
    except IndexError:
        # finished
        pass
    return count_of_xmas


def find_xmas_other_way(data: StreamOfLines, pattern: SearchPattern) -> CountOfXmas:
    count: int = 0
    block_idx: int
    stack: list[SearchBlock] = [[], [], [], []]
    for line_idx, line in enumerate(data):
        for block_idx, search_block in enumerate(stack):
            if is_interesting_block(block_idx, line_idx):
                search_block.append(line)
            if len(search_block) == 4:
                # forward
                count += search_block_vertical(search_block, pattern)
                # backward
                count += search_block_vertical(search_block, pattern[::-1])
                stack[block_idx] = []
    return count


def find_xmas_crazy(data: typing.Iterator[StreamOfLines]) -> CountOfXmas:
    count: int = 0
    count += find_xmas_horizontal(next(data))
    count += find_xmas_other_way(next(data), [(0, "x"), (0, "m"), (0, "a"), (0, "s")])
    count += find_xmas_other_way(next(data), [(0, "x"), (1, "m"), (2, "a"), (3, "s")])
    count += find_xmas_other_way(next(data), [(0, "s"), (1, "a"), (2, "m"), (3, "x")])
    return count


def main(args: argparse.Namespace):
    summary_of_count_of_xmas: CountOfXmas

    sum_count_of_xmas: SumCountOfXmas
    match args.mode:
        case _:
            sum_count_of_xmas = find_xmas_crazy

    summary_of_count_of_xmas = sum_count_of_xmas(create_stream_of_lines(args.file_path))

    print(f"Summary of multiplications added by <{args.mode}>: ", summary_of_count_of_xmas)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        "Count all XMAS in all directions - horizontal, vertical, diagonal and ... reversed."
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["crazy"],
        default="crazy",
        help="Mode of counting",
    )

    parse_args_run_and_profile(parser, main)
