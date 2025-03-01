import typing
import argparse
import re

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    MemRecord,
    MemRecords,
    ReadingMemRecords,
    read_mem_records_from_file,
)


Summary: typing.TypeAlias = int


class AddMultiplications(typing.Protocol):
    def __call__(self, records: MemRecords) -> Summary: ...


def simplify_record_of_memory(record: MemRecord) -> MemRecord:
    return record.replace("|", "x").replace("do()", "|").replace("!", "x").replace("don't()", "!")


def count_flag_enabled(idx: int, disabled_parts: list[str], enabled_parts: list[str], flag_enabled: bool) -> bool:
    if idx + 1 == len(disabled_parts):
        # it is the last piece from pieces in given record
        if len(enabled_parts) > 1:
            # we have a command to enable mul for next record
            flag_enabled = True
        elif len(disabled_parts) > 1:
            # we have a command to disable mul for next record
            flag_enabled = False
    else:
        # it is the piece from pieces, not the last of them in given record
        flag_enabled = False
    return flag_enabled


def find_enabled_parts(record: MemRecord, flag_enabled: bool) -> tuple[MemRecords, bool]:
    enabled_parts: MemRecords = []
    disabled_pieces: list[str] = record.split("!")
    for idx, disabled_piece in enumerate(disabled_pieces):
        enabled_pieces = disabled_piece.split("|")
        if flag_enabled is True:
            enabled_parts += enabled_pieces[:]
        else:
            enabled_parts += enabled_pieces[1:]
        flag_enabled = count_flag_enabled(idx, disabled_pieces, enabled_pieces, flag_enabled)
    return enabled_parts, flag_enabled


def add_multiplications_by_regex(records: MemRecords) -> Summary:
    summary: Summary = 0
    flag_enabled: bool = True
    for record in records:
        record = simplify_record_of_memory(record)
        enabled_parts: MemRecords
        enabled_parts, flag_enabled = find_enabled_parts(record, flag_enabled)
        for enabled_part in enabled_parts:
            for match in re.finditer(r"mul\((\d{1,3}),(\d{1,3})\)", enabled_part):
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
        "Sum all valid multiplications in a given "
        "file (and in enabled piece of memory - do() x don't()) - example of multiplication: mul(12,13)"
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["regex"],
        default="regex",
        help="Mode of summary: regex",
    )

    parse_args_run_and_profile(parser, main)
