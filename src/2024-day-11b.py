import typing
from functools import lru_cache
from collections import Counter


FilePath: typing.TypeAlias = str
StreamOfLines: typing.TypeAlias = typing.Iterator[str]


class OpenStream(typing.Protocol):
    def __call__(self, file: FilePath) -> StreamOfLines: ...


def stream_opener(file: FilePath) -> StreamOfLines:
    with open(file) as file_handler:
        for line in file_handler:
            yield line


read_char: OpenStream = stream_opener


Arrangement: typing.TypeAlias = tuple[str, ...]
Stones: typing.TypeAlias = Counter[str]


@lru_cache(maxsize=None)
def transform(stone: str) -> Arrangement:
    if stone == "0":
        return ("1",)
    if len(stone) % 2 == 0:
        # number of digits in new stone
        nod = len(stone) // 2
        left_stone = str(int(stone[:nod]))
        right_stone = str(int(stone[nod:]))
        return left_stone, right_stone
    return (str(int(stone) * 2024),)


def blink(_stones: Stones) -> Stones:
    new_stones: Stones = Counter()
    for stone, count in _stones.items():
        for _stone in transform(stone):
            new_stones[_stone] += count
    return new_stones


numbers: list[str] = []
for line in read_char("../media/2024-day-11.input"):
    numbers += line.strip().split(" ")

print(numbers)


stones = Counter(numbers)
for _ in range(75):
    stones = blink(stones)

print(f"Count of stones: {sum(stones.values())}")
