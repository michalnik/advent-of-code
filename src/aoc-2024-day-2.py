import argparse
import typing
from rich import print

from utils import (
    validate_file_path,
    create_arg_parser,
    parse_args_run_and_profile,
    ReadingReports,
    Reports,
    read_reports_from_file,
)


ReportsSafeCount: typing.TypeAlias = int


class EvaluateSafeCount(typing.Protocol):
    def __call__(self, reports: Reports) -> ReportsSafeCount: ...


def count_dec_or_inc(level: int, last_level: int, dec_or_inc: typing.Optional[int]) -> int:
    # levels decreasing and increasing in tuples
    dec = (-1, -2, -3)
    inc = (1, 2, 3)

    delta: int = level - last_level
    # find out if it is decreasing/increasing or steady level
    if dec_or_inc is None:
        return 1 if delta in inc else 2 if delta in dec else 0
    else:
        return (
            1
            if dec_or_inc == 1 and delta in inc
            else (
                2
                if dec_or_inc == 2 and delta in dec
                else (-1 if dec_or_inc == 1 and delta in dec else -2 if dec_or_inc == 2 and delta in inc else 0)
            )
        )


def evaluate_safe_count_by_logical(reports: Reports) -> ReportsSafeCount:
    safe_count: ReportsSafeCount = 0
    for report in reports:
        dec_or_inc: typing.Optional[int] = None
        last_level: typing.Optional[int] = None
        for level in report:
            if last_level is None:
                # first round, remember the last level
                last_level = level
                continue
            else:
                dec_or_inc = count_dec_or_inc(level, last_level, dec_or_inc)
            if dec_or_inc is not None and dec_or_inc <= 0:
                # it is not safe report
                #     0 - nor increase or decrease for current level
                #    -1 - at first increasing observed and now decreasing
                #    -2 - at first decreasing observed and now increasing
                break
            last_level = level
        else:
            safe_count += 1
    return safe_count


def evaluate_safe_count_by_sets(reports: Reports) -> ReportsSafeCount:
    safe_count: ReportsSafeCount = 0
    report_level_diffs: set[int]
    for report in reports:
        report_level_diffs = {level2 - level1 for level1, level2 in zip(report, report[1:])}
        if all(0 < diff < 4 for diff in report_level_diffs) or all(0 > diff > -4 for diff in report_level_diffs):
            safe_count += 1
    return safe_count


def main(args: argparse.Namespace):
    safe_count: ReportsSafeCount

    read_reports: ReadingReports
    match args.mode:
        case _:
            read_reports = read_reports_from_file

    reports: Reports = read_reports(args.file_path)

    evaluate_safe_count: EvaluateSafeCount
    match args.mode:
        case "sets":
            evaluate_safe_count = evaluate_safe_count_by_sets
        case _:
            evaluate_safe_count = evaluate_safe_count_by_logical

    safe_count = evaluate_safe_count(reports)

    print(f"Safe reports count evaluated by <{args.mode}>: ", safe_count)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        "Evaluation of data in a given file regards of - how many reports are safe."
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["logical", "sets"],
        default="logical",
        help="Mode of evaluation: logical (default: logical)",
    )

    parse_args_run_and_profile(parser, main)
