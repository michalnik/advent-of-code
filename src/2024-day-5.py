import argparse
import typing
import math
from dataclasses import dataclass

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    StreamOfLines,
    create_stream_of_lines,
)


SUMMARY: typing.TypeAlias = int


@dataclass
class RULE:
    page: int
    before: int | None
    after: int | None


@dataclass
class RULES:
    rules: list[RULE]

    def find_rules(self, page: int) -> list[RULE]:
        rules: list[RULE] = []
        for rule in self.rules:
            if rule.page == page:
                rules.append(rule)
        return rules

    def add_rule_from_line(self, line: str):
        page_fst: int
        page_snd: int
        page_fst, page_snd = [int(page) for page in line.split("|")]
        self.rules.append(RULE(page=page_fst, before=None, after=page_snd))
        self.rules.append(RULE(page=page_snd, before=page_fst, after=None))


@dataclass
class UPDATE:
    update: list[int]

    def __init__(self, line: str):
        self.update = list(int(char) for char in line.split(","))

    def is_correct_rule(self, page: int, rule: RULE) -> bool:
        correct: bool = True
        if rule.after and rule.after in self.update[: self.update.index(page)]:
            correct = False
        if rule.before and rule.before in self.update[self.update.index(page) :]:
            correct = False
        return correct

    def is_correct_for_page(self, page: int, rules: RULES) -> bool:
        correct: bool = True
        page_rules: list[RULE] = rules.find_rules(page)
        for rule in page_rules:
            if not self.is_correct_rule(page, rule):
                correct = False
        return correct

    def is_correct(self, rules: RULES) -> bool:
        correct: bool = True
        for page in self.update:
            if not self.is_correct_for_page(page, rules):
                correct = False
        return correct

    def find_middle_page_number(self) -> int:
        middle: int = math.floor(len(self.update) / 2)
        return self.update[middle]


class AddingUpMiddlePageNumbersOfCorrectlyOrderedUpdates(typing.Protocol):
    def __call__(self, stream: typing.Iterator[StreamOfLines]) -> SUMMARY: ...


def add_up_middle_page_numbers(stream: typing.Iterator[StreamOfLines]) -> SUMMARY:
    summary: SUMMARY = 0
    is_rule: bool = True
    rules: RULES = RULES(rules=[])
    update: UPDATE
    lines: StreamOfLines = next(stream)
    for line in lines:
        if not line.strip():
            is_rule = False
            continue
        if is_rule:
            rules.add_rule_from_line(line)
        else:
            # it is update
            update = UPDATE(line=line)
            if update.is_correct(rules):
                summary += update.find_middle_page_number()
    return summary


def main(args: argparse.Namespace):
    summary: SUMMARY

    adding_up_middle_page_numbers: AddingUpMiddlePageNumbersOfCorrectlyOrderedUpdates
    match args.mode:
        case _:
            adding_up_middle_page_numbers = add_up_middle_page_numbers

    summary = adding_up_middle_page_numbers(create_stream_of_lines(args.file_path))

    print(f"Added up middle page numbers correctly ordered updates by mode <{args.mode}>: ", summary)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        "Validate order of updates and finally add middle page numbers from\n" "correctly ordered updates."
    )
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["default"],
        default="default",
        help="Mode of adding",
    )

    parse_args_run_and_profile(parser, main)
