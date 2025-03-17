import typing
import os
import sys
import argparse
import cProfile
import pstats
from rich import print
import numpy as np


def create_arg_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--rows", type=int, default=10, help="Number of rows of profiler stats to print")
    return parser


def validate_file_path(path: str) -> str:
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File '{path}' does not exist or it is not a file.")
    return path


def parse_args_run_and_profile(parser: argparse.ArgumentParser, main: typing.Callable[[argparse.Namespace], None]):
    args_from_cli = parser.parse_args()
    print("These input arguments were received: ", args_from_cli)

    with cProfile.Profile() as profile:
        main(args_from_cli)

    print("\nUsing cProfile ...")
    stats = pstats.Stats(profile)
    stats.strip_dirs().sort_stats("time").print_stats(args_from_cli.rows)

    sys.exit(0)


FilePath: typing.TypeAlias = str
LocationList: typing.TypeAlias = list[int]
DistanceList: typing.TypeAlias = list[int]


class GatheredLocations(typing.TypedDict):
    first: LocationList
    second: LocationList


Locations: typing.TypeAlias = GatheredLocations | np.typing.NDArray[np.int_]
ReportLevel: typing.TypeAlias = int
Report: typing.TypeAlias = list[int]
Reports: typing.TypeAlias = list[Report]
MemRecord: typing.TypeAlias = str
MemRecords: typing.TypeAlias = list[MemRecord]
StreamOfLines: typing.TypeAlias = typing.Iterator[str]


class ReadingLocations(typing.Protocol):
    def __call__(self, file: FilePath) -> Locations: ...


class ReadingReports(typing.Protocol):
    def __call__(self, file: FilePath) -> Reports: ...


class ReadingMemRecords(typing.Protocol):
    def __call__(self, file: FilePath) -> MemRecords: ...


class OpenStreamOfLines(typing.Protocol):
    def __call__(self, file: FilePath) -> StreamOfLines: ...


class CreateStreamOfLines(typing.Protocol):
    def __call__(self, file: FilePath) -> typing.Iterator[StreamOfLines]: ...


def read_locations_from_file(file: FilePath) -> Locations:
    _first: LocationList = []
    _second: LocationList = []
    with open(file) as file_handler:
        for line in file_handler:
            locations = list(
                part
                for part in (int(line_part) if bool(line_part.strip()) else None for line_part in line.split(" "))
                if part is not None
            )
            _first.append(locations[0])
            _second.append(locations[1])

    return GatheredLocations(first=_first, second=_second)


def numpy_read_locations(file: FilePath) -> Locations:
    return np.loadtxt(file, dtype=int)


def read_reports_from_file(file: FilePath) -> Reports:
    reports: Reports = []
    with open(file) as file_handler:
        for line in file_handler:
            report: Report = list(
                level
                for level in (int(line_part) if bool(line_part.strip()) else None for line_part in line.split(" "))
                if level is not None
            )
            reports.append(report)

    return reports


def read_mem_records_from_file(file: FilePath) -> MemRecords:
    records: MemRecords = []
    with open(file) as file_handler:
        for line in file_handler:
            record: MemRecord = line
            records.append(record)
    return records


def open_stream_of_lines(file: FilePath) -> StreamOfLines:
    with open(file) as file_handler:
        yield from file_handler


def create_stream_of_lines(file: FilePath) -> typing.Iterator[StreamOfLines]:
    while True:
        yield open_stream_of_lines(file)


def sort_locations(locs: Locations):
    if isinstance(locs, dict):
        locs["first"].sort()
        locs["second"].sort()
    else:
        raise TypeError("Wrong locations passed - wrong type")
