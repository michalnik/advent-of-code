import typing
import argparse
import os
import sys
import pstats
import cProfile
from rich import print
import numpy as np


FilePath: typing.TypeAlias = str
LocationList: typing.TypeAlias = list[int]
DistanceList: typing.TypeAlias = list[int]
TotalDistance: typing.TypeAlias = int


class GatheredLocations(typing.TypedDict):
    first: LocationList
    second: LocationList


class ReadingLocations(typing.Protocol):
    def __call__(self, file: FilePath) -> GatheredLocations: ...


class EvaluateTotalDistance(typing.Protocol):
    def __call__(self, locations: GatheredLocations) -> TotalDistance: ...


def read_file(file: FilePath) -> GatheredLocations:
    _first: LocationList = []
    _second: LocationList = []
    with open(file) as file_handler:
        for line in file_handler.readlines():
            locations = list(
                part for part in (
                    int(line_part) if bool(line_part.strip()) else None for line_part in line.split(" ")
                ) if part is not None
            )
            _first.append(locations[0])
            _second.append(locations[1])

    return GatheredLocations(first=_first, second=_second)


def evaluate_total_distance_by_comprehension(locations: GatheredLocations) -> TotalDistance:
    return sum(abs(_first - _second) for _first, _second in zip(locations["first"], locations["second"]))


def evaluate_total_distance_by_functional(locations: GatheredLocations) -> TotalDistance:
    return sum(map(lambda left, right: abs(left - right), locations["first"], locations["second"]))


def validate_file_path(path: str) -> str:
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File '{path}' does not exist or it is not a file.")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluation of 2 paths(list of locations) - total length.")
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["comprehension", "functional", "numpy"],
        default="comprehension",
        help="Mode of evaluation: comprehension, functional or numpy (default: comprehension)"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=10,
        help="Number of rows of profiler stats to print"
    )
    args = parser.parse_args()
    print("These input arguments were received: ", args)

    total_distance: TotalDistance

    with cProfile.Profile() as profile:
        if args.mode == "numpy":
            data = np.loadtxt(args.file_path, dtype=int)
            first, second = data[:, 0], data[:, 1]
            total_distance = np.sum(np.abs(np.sort(first) - np.sort(second)))
        else:
            read_locations: ReadingLocations = read_file
            locs: GatheredLocations = read_locations(args.file_path)
            locs["first"].sort()
            locs["second"].sort()

            evaluate_total_distance: EvaluateTotalDistance
            match args.mode:
                case "functional":
                    evaluate_total_distance = evaluate_total_distance_by_functional
                case _:
                    evaluate_total_distance = evaluate_total_distance_by_comprehension

            total_distance = evaluate_total_distance(locs)

    print(f"Total distance evaluated by <{args.mode}>: ", total_distance)

    print("\nUsing cProfile ...")
    stats = pstats.Stats(profile)
    stats.strip_dirs().sort_stats("time").print_stats(args.rows)

    sys.exit(0)
