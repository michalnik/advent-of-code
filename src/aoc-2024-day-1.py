import argparse
import typing
from rich import print
import numpy as np

from utils import (
    validate_file_path,
    create_arg_parser,
    parse_args_run_and_profile,
    Locations,
    ReadingLocations,
    read_and_parse_file,
    np_load_data,
)


TotalDistance: typing.TypeAlias = int


class EvaluateTotalDistance(typing.Protocol):
    def __call__(self, locations: Locations) -> TotalDistance: ...


def sort_locations(locs: Locations):
    if isinstance(locs, dict):
        locs["first"].sort()
        locs["second"].sort()
    else:
        raise TypeError("Wrong locations passed - wrong type")


def evaluate_total_distance_by_comprehension(locations: Locations) -> TotalDistance:
    sort_locations(locations)
    if isinstance(locations, dict):
        return sum(abs(_first - _second) for _first, _second in zip(locations["first"], locations["second"]))
    else:
        # just return error distance
        raise TypeError("Wrong locations passed - wrong type")


def evaluate_total_distance_by_functional(locations: Locations) -> TotalDistance:
    sort_locations(locations)
    if isinstance(locations, dict):
        return sum(map(lambda left, right: abs(left - right), locations["first"], locations["second"]))
    else:
        # just return error distance
        raise TypeError("Wrong locations passed - wrong type")


def evaluate_total_distance_by_numpy(locations: Locations) -> TotalDistance:
    if isinstance(locations, np.ndarray):
        first, second = locations[:, 0], locations[:, 1]
        return np.sum(np.abs(np.sort(first) - np.sort(second)))
    else:
        # just return error distance
        raise TypeError("Wrong locations passed - wrong type")


def main(args: argparse.Namespace):
    total_distance: TotalDistance

    read_locations: ReadingLocations
    match args.mode:
        case "numpy":
            read_locations = np_load_data
        case _:
            read_locations = read_and_parse_file

    locs: Locations = read_locations(args.file_path)

    evaluate_total_distance: EvaluateTotalDistance
    match args.mode:
        case "numpy":
            evaluate_total_distance = evaluate_total_distance_by_numpy
        case "functional":
            evaluate_total_distance = evaluate_total_distance_by_functional
        case _:
            evaluate_total_distance = evaluate_total_distance_by_comprehension

    total_distance = evaluate_total_distance(locs)

    print(f"Total distance evaluated by <{args.mode}>: ", total_distance)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser("Evaluation of 2 paths(list of locations) - total length.")
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["comprehension", "functional", "numpy"],
        default="comprehension",
        help="Mode of evaluation: comprehension, functional or numpy (default: comprehension)",
    )

    parse_args_run_and_profile(parser, main)
