import typing

from abc import ABC, abstractmethod
from dataclasses import dataclass

FilePath: typing.TypeAlias = str
StreamOfLines: typing.TypeAlias = typing.Iterator[str]


class OpenStream(typing.Protocol):
    def __call__(self, file: FilePath) -> StreamOfLines: ...


def stream_opener(file: FilePath) -> StreamOfLines:
    with open(file) as file_handler:
        for line in file_handler:
            yield line


read_char: OpenStream = stream_opener


@dataclass
class Arrangement:
    numbers: list[int]

    def add_number(self, number: int):
        self.numbers.append(number)

    def load_numbers(self, file_opener: OpenStream, file_path: FilePath):
        for line in file_opener(file_path):
            for word in line.strip().split(" "):
                number = int(word)
                self.add_number(number)


class Rule(ABC):
    @abstractmethod
    def apply(self, number: int) -> Arrangement: ...


class ZeroRule(Rule):
    def apply(self, number: int) -> Arrangement:
        if number == 0:
            return Arrangement(numbers=[1])
        else:
            raise ValueError(f"The rule: {self.__class__.__name__} cannot apply on number: {number}")


class EvenRule(Rule):
    def apply(self, number: int) -> Arrangement:
        new_arrangement: Arrangement = Arrangement(numbers=[])
        _number: str = str(number)
        length: int = len(_number)
        if length % 2 == 0:
            nod = int(length / 2)
            new_arrangement.add_number(int(_number[:nod]))
            new_arrangement.add_number(int(_number[nod:]))
            return new_arrangement
        else:
            raise ValueError(f"The rule: {self.__class__.__name__} cannot apply on number: {number}")


class MultipleRule(Rule):
    def apply(self, number: int) -> Arrangement:
        return Arrangement(numbers=[2024 * number])


@dataclass
class AppRules[T: Rule]:
    rules: list[T]

    def apply_rules(self, blink_arrangement: Arrangement, stone: int):
        for rule in self.rules:
            try:
                rule_arrangement = rule.apply(stone)
            except ValueError:
                continue
            else:
                self.add_rule_arrangement(blink_arrangement, rule_arrangement)
                break

    @staticmethod
    def add_rule_arrangement(blink_arrangement: Arrangement, rule_arrangement: Arrangement):
        for _number in rule_arrangement.numbers:
            blink_arrangement.add_number(_number)

    def blink(self, old_arrangement: Arrangement) -> Arrangement:
        blink_arrangement: Arrangement = Arrangement(numbers=[])
        for stone in old_arrangement.numbers:
            self.apply_rules(blink_arrangement, stone)
        return blink_arrangement


if __name__ == "__main__":
    arrangement = Arrangement(numbers=[])
    arrangement.load_numbers(read_char, "../media/2024-day-11.input")

    zero_rule = ZeroRule()
    even_rule = EvenRule()
    multiple_rule = MultipleRule()
    app_rules = AppRules(rules=[zero_rule, even_rule, multiple_rule])

    number_of_blinks: int = 25
    for idx, _ in enumerate(range(number_of_blinks)):
        arrangement = app_rules.blink(arrangement)

    print(len(arrangement.numbers))
