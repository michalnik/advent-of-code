import typing
import argparse
from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    Reports,
    ReadingReports,
    read_reports_from_file,
)


ReportsSafeCount: typing.TypeAlias = int


class EvaluateSafeCount(typing.Protocol):
    def __call__(self, reports: Reports) -> ReportsSafeCount: ...


def evaluate_safe_count_by_sets(reports: Reports) -> ReportsSafeCount:
    safe_count: ReportsSafeCount = 0
    report_level_diffs: set[int]
    for rep in reports:
        for idx in range(len(rep)):
            report = rep.copy()
            report.pop(idx)
            report_level_diffs = {level2 - level1 for level1, level2 in zip(report, report[1:])}
            if all(0 < diff < 4 for diff in report_level_diffs) or all(0 > diff > -4 for diff in report_level_diffs):
                safe_count += 1
                break
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
            evaluate_safe_count = evaluate_safe_count_by_sets
    safe_count = evaluate_safe_count(reports)

    print(f"Safe reports count evaluated by <{args.mode}>: ", safe_count)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        "Evaluation of data in a given file regards of - how many reports are safe(with Problem Dampener)."
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["sets"],
        default="sets",
        help="Mode of evaluation",
    )

    parse_args_run_and_profile(parser, main)
