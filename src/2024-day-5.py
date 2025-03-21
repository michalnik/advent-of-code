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

    def make_correct(self, page: int, rule: RULE):
        position: int = self.update.index(page)
        if rule.after and rule.after in self.update[:position]:
            self.update.remove(rule.after)
            self.update.insert(position + 2, rule.after)
        position = self.update.index(page)
        if rule.before and rule.before in self.update[position:]:
            self.update.remove(rule.before)
            self.update.insert(position, rule.before)

    def find_middle_page_number(self) -> int:
        middle: int = math.floor(len(self.update) / 2)
        return self.update[middle]

    def correct(self, rules: RULES):
        page_rules: list[RULE]
        while not self.is_correct(rules):
            for page in self.update:
                page_rules = rules.find_rules(page)
                for rule in page_rules:
                    if not self.is_correct_rule(page, rule):
                        self.make_correct(page, rule)


class AddingUpMiddlePageNumbersOfCorrectlyOrderedUpdates(typing.Protocol):
    def __call__(self, stream: typing.Iterator[StreamOfLines]) -> SUMMARY: ...


def find_middle_page_number(update: UPDATE, rules: RULES, add_mode: str) -> SUMMARY:
    summary: SUMMARY = 0
    correct_update: bool = update.is_correct(rules)
    if correct_update and add_mode == "correct":
        summary += update.find_middle_page_number()
    elif not correct_update and add_mode == "incorrect":
        update.correct(rules)
        summary += update.find_middle_page_number()
    return summary


def add_up_middle_page_numbers(stream: typing.Iterator[StreamOfLines], add_mode: str = "correct") -> SUMMARY:
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
            # it is an update line now
            update = UPDATE(line=line)
            summary += find_middle_page_number(update, rules, add_mode)
    return summary


def add_up_middle_page_numbers_incorrect(stream: typing.Iterator[StreamOfLines]) -> SUMMARY:
    summary: SUMMARY = 0
    summary += add_up_middle_page_numbers(stream, add_mode="incorrect")
    return summary


def main(args: argparse.Namespace):
    summary: SUMMARY

    adding_up_middle_page_numbers: AddingUpMiddlePageNumbersOfCorrectlyOrderedUpdates
    match args.mode:
        case "incorrect":
            adding_up_middle_page_numbers = add_up_middle_page_numbers_incorrect
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
        choices=["correct", "incorrect"],
        default="correct",
        help="Mode of adding (from correctly/incorrectly ordered updates",
    )

    parse_args_run_and_profile(parser, main)
