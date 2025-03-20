import argparse
import typing
import itertools
import functools

from utils import (
    create_arg_parser,
    validate_file_path,
    parse_args_run_and_profile,
    StreamOfLines,
    create_stream_of_lines,
)


SummaryOfPassed: typing.TypeAlias = int
Operator: typing.TypeAlias = typing.Literal["+", "*"]


POSSIBLE_OPERATORS: list[str] = list(typing.get_args(Operator))


class EquationPass(typing.Protocol):
    def __call__(self, line: str) -> SummaryOfPassed: ...


class AddingUpEquations(typing.Protocol):
    def __call__(self, stream: typing.Iterator[StreamOfLines], test_equation: EquationPass) -> SummaryOfPassed: ...


def equation_pass(line: str) -> SummaryOfPassed:
    summary: SummaryOfPassed = 0
    left_side, numbers = line.split(":")
    args: list[int] = [int(arg) for arg in numbers.split(" ") if arg != ""]
    products: itertools.product[tuple[str, ...]] = itertools.product(["+", "*"], repeat=len(args) - 1)
    for product in products:
        right_side: int = functools.reduce(
            lambda res, params: res + params[0] if params[1] == "+" else res * params[0],
            zip(args[1:], product),
            args[0],
        )
        if int(left_side) == right_side:
            summary += right_side
            break
    return summary


def adding_up_equations_by_default(
    stream: typing.Iterator[StreamOfLines], test_equation: EquationPass
) -> SummaryOfPassed:
    summary_of_passed: SummaryOfPassed = 0
    for line in next(stream):
        summary_of_passed += test_equation(line.strip())
    return summary_of_passed


def main(args: argparse.Namespace):
    summary_of_passed: SummaryOfPassed = 0
    stream: typing.Iterator[StreamOfLines] = create_stream_of_lines(args.file_path)

    adding_up_equations: AddingUpEquations
    test_equation: EquationPass
    match args.mode:
        case _:
            test_equation = equation_pass
            adding_up_equations = adding_up_equations_by_default

    summary_of_passed += adding_up_equations(stream, test_equation)
    print(f"Added up passed equations by mode <{args.mode}>: ", summary_of_passed)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser(
        (
            "Go through calibration equations and count summary of left side of equations that offer\n"
            "at least one of product of operators '+' and '*' which can be used to reach test value.\n\n"
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
