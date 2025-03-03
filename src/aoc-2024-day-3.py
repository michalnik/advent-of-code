import typing
import argparse
import re

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    MemRecords,
    ReadingMemRecords,
    read_mem_records_from_file,
)


Summary: typing.TypeAlias = int


class AddMultiplications(typing.Protocol):
    def __call__(self, records: MemRecords) -> Summary: ...


def add_multiplications_by_regex(records: MemRecords) -> Summary:
    summary: Summary = 0
    for record in records:
        for match in re.finditer(r"mul\((\d{1,3}),(\d{1,3})\)", record):
            left, right = match.groups()
            summary += int(left) * int(right)
    return summary


def main(args: argparse.Namespace):
    summary: Summary

    read_mem_records: ReadingMemRecords
    match args.mode:
        case _:
            read_mem_records = read_mem_records_from_file

    mem_records: MemRecords = read_mem_records(args.file_path)

    add_multiplications: AddMultiplications
    match args.mode:
        case _:
            add_multiplications = add_multiplications_by_regex

    summary = add_multiplications(mem_records)

    print(f"Summary of multiplications added by <{args.mode}>: ", summary)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        "Sum all valid multiplications in a given file - example of multiplication: mul(12,13)"
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["regex"],
        default="regex",
        help="Mode of summary",
    )

    parse_args_run_and_profile(parser, main)
