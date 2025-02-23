import argparse
import typing
from rich import print

from utils import (
    validate_file_path,
    create_arg_parser,
    parse_args_run_and_profile,
    Locations,
    ReadingLocations,
    read_locations_from_file,
    numpy_read_locations,
)


SimilarityScore: typing.TypeAlias = int


class EvaluateSimilarityScore(typing.Protocol):
    def __call__(self, locations: Locations) -> SimilarityScore: ...


def evaluate_similarity_score_by_count(locations: Locations) -> SimilarityScore:
    similarity_score: SimilarityScore = 0
    if isinstance(locations, dict):
        for value in locations["first"]:
            similarity_score += value * locations["second"].count(value)
        return similarity_score
    else:
        raise TypeError("Wrong locations passed - wrong type")


def main(args: argparse.Namespace):
    similarity_score: SimilarityScore

    read_locations: ReadingLocations
    match args.mode:
        case "numpy":
            read_locations = numpy_read_locations
        case _:
            read_locations = read_locations_from_file

    locs: Locations = read_locations(args.file_path)

    evaluate_similarity_score: EvaluateSimilarityScore
    match args.mode:
        case "count":
            evaluate_similarity_score = evaluate_similarity_score_by_count
        case _:

            def evaluate(locations: Locations) -> SimilarityScore:
                print(locations)
                return -1

            evaluate_similarity_score = evaluate

    similarity_score = evaluate_similarity_score(locs)

    print(f"Similarity score evaluated by <{args.mode}>: ", similarity_score)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = create_arg_parser("Evaluation of 2 paths(list of locations) - similarity score.")
    parser.add_argument("file_path", type=validate_file_path, help="Existing file path")
    parser.add_argument(
        "--mode",
        choices=["numpy", "count"],
        default="numpy",
        help="Mode of evaluation: numpy (default: numpy)",
    )

    parse_args_run_and_profile(parser, main)
