#!/usr/bin/env python
# coding: utf-8
import typing
from dataclasses import dataclass, field
from rich import print


FilePath: typing.TypeAlias = str
FileContent: typing.TypeAlias = list[str]
Grid: typing.TypeAlias = list[list[str]]
Visited: typing.TypeAlias = list[list[bool]]


@dataclass
class Business:
    region: str
    area: int = 0
    perimeter: int = 0
    border: int = 0
    price: int = 0
    price_with_discount: int = 0

    def __post_init__(self):
        self.price = self.area * self.perimeter
        self.price_with_discount = self.area * self.border


@dataclass
class Pricing:
    regions: list[Business] = field(default_factory=list)

    def total_price(self) -> int:
        price = 0
        for region in self.regions:
            price += region.price
        return price

    def total_price_with_discount(self) -> int:
        price = 0
        for region in self.regions:
            price += region.price_with_discount
        return price


class FileReader(typing.Protocol):
    def __call__(self, file: FilePath) -> FileContent: ...


def file_reader(file: FilePath) -> FileContent:
    with open(file) as file_handler:
        return [line for line in file_handler.read().splitlines(keepends=False) if len(line) > 0]


data_reader: FileReader = file_reader


_grid: Grid = []
_price: Pricing = Pricing()
_file_content: FileContent = file_reader("../media/2024-day-12.input")

for row, line in enumerate(_file_content):
    for col, letter in enumerate(line):
        if col == 0:
            _grid.append([letter])
        else:
            _grid[row].append(letter)


_visited: Visited = [[False for _ in row] for row in _grid]


Side: typing.TypeAlias = tuple[tuple[int, int], tuple[int, int]]


def create_side(x: int, y: int, dx: int, dy: int) -> Side:
    if dx != 0:
        return (x, y), (x, y - dx)
    if dy != 0:
        return (x, y), (x + dy, y)
    raise ValueError("Wrong direction for create side!")


def one_side(fst_side: Side, snd_side: Side) -> bool:
    fst_start, fst_end = fst_side
    snd_start, snd_end = snd_side

    if fst_start[1] == fst_end[1] == snd_start[1] == snd_end[1]:
        # points on the same horizontal line
        dir_a = fst_end[0] - fst_start[0]
        dir_b = snd_end[0] - snd_start[0]
        if dir_a * dir_b < 0:
            # cannot merge sides with opposite direction
            return False

        # assure one end is shared and the other one is different
        return (fst_start == snd_end and fst_end != snd_start) or (fst_end == snd_start and fst_start != snd_end)

    # same code for the vertical
    if fst_start[0] == fst_end[0] == snd_start[0] == snd_end[0]:
        dir_a = fst_end[1] - fst_start[1]
        dir_b = snd_end[1] - snd_start[1]
        if dir_a * dir_b < 0:
            return False
        return (fst_start == snd_end and fst_end != snd_start) or (fst_end == snd_start and fst_start != snd_end)

    # others sides are not mergeable
    return False


def merge_side(fst_side: Side, snd_side: Side) -> Side:
    if fst_side[0] == snd_side[1]:
        # backward direction -> turnaround
        tmp_side = fst_side
        fst_side = snd_side
        snd_side = tmp_side
    return (fst_side[0][0], fst_side[0][1]), (snd_side[1][0], snd_side[1][1])


def reduce_sides(sides: set[Side]):  # noqa[C901] [8]
    init = True
    to_merge: list[Side] = []
    while to_merge or init:
        init = False
        if to_merge:
            sides.remove(to_merge[0])
            sides.remove(to_merge[1])
            new_side = merge_side(to_merge[0], to_merge[1])
            sides.add(new_side)
            to_merge = []
        for fst_side in sides:
            for snd_side in sides:
                if fst_side == snd_side:
                    continue
                if one_side(fst_side, snd_side):
                    to_merge = [fst_side, snd_side]
                    break
            if to_merge:
                break


def flood_fill(  # noqa[C901] (7)
    grid: list[list[str]], x: int, y: int, visited: list[list[bool]], region: str
) -> tuple[int, int, int]:
    """It will search area of items with value "region" to return size of new region, perimeter and count of sides
    It'll begin in point (x, y).

    :param grid: the whole grid with all the garden plots
    :param x: the x coordinate
    :param y: the y coordinate
    :param visited: the visited list with all visited areas marked as True
    :param region: the type of plant growing in a plot
    :returns
        size of region (count of plots), region perimeter, region count of sides
    """
    rows, cols = len(grid), len(grid[0])
    stack = [(x, y)]  # area to search(dynamically grows with other plot)
    area = 0
    perimeter = 0
    sides: set[Side] = set()

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    while stack:
        cx, cy = stack.pop()
        if visited[cx][cy]:
            # already counted that plot
            continue
        visited[cx][cy] = True
        area += 1

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                # validation is ok (being in grid)
                if grid[nx][ny] == region:
                    if not visited[nx][ny]:
                        # it is a new area within the same region
                        stack.append((nx, ny))
                else:
                    perimeter += 1
                    sides.add(create_side(nx, ny, dx, dy))
            else:
                perimeter += 1
                sides.add(create_side(nx, ny, dx, dy))

    reduce_sides(sides)

    return area, perimeter, len(sides)


for i in range(len(_grid)):
    for j in range(len(_grid[0])):
        if not _visited[i][j]:
            _region = _grid[i][j]
            size, _perimeter, _border = flood_fill(_grid, i, j, _visited, _region)
            _price.regions.append(Business(region=_region, area=size, perimeter=_perimeter, border=_border))


print(_price, "\n")
print("Total price: ", _price.total_price(), "\n")
print("Total price with discount: ", _price.total_price_with_discount(), "\n")
