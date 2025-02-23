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


def evaluate_safe_count_by_functional(reports: Reports) -> ReportsSafeCount:  # noqa: C901[6]
    safe_count: ReportsSafeCount = 0
    dec = (-1, -2, -3)
    inc = (1, 2, 3)
    for report in reports:
        dec_or_inc = None
        last_level = None
        for level in report:
            if last_level is None:
                # first round, remember the last level
                last_level = level
                continue
            else:
                delta = level - last_level
                # find out if it is decreasing/increasing or steady level
                if dec_or_inc is None:
                    dec_or_inc = 1 if delta in inc else 2 if delta in dec else 0
                else:
                    dec_or_inc = (
                        1
                        if dec_or_inc == 1 and delta in inc
                        else (
                            2
                            if dec_or_inc == 2 and delta in dec
                            else (
                                -1
                                if dec_or_inc == 1 and delta in dec
                                else -2 if dec_or_inc == 2 and delta in inc else 0
                            )
                        )
                    )
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


def main(args: argparse.Namespace):
    safe_count: ReportsSafeCount

    read_reports: ReadingReports
    match args.mode:
        case _:
            read_reports = read_reports_from_file

    reports: Reports = read_reports(args.file_path)

    evaluate_safe_count: EvaluateSafeCount
    match args.mode:
        case _:
            evaluate_safe_count = evaluate_safe_count_by_functional

    safe_count = evaluate_safe_count(reports)

    print(f"Safe reports count evaluated by <{args.mode}>: ", safe_count)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        "Evaluation of data in a given file regards of - how many reports are safe."
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["functional"],
        default="functional",
        help="Mode of evaluation: functional (default: functional)",
    )

    parse_args_run_and_profile(parser, main)
