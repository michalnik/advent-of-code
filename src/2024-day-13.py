import typing
from dataclasses import dataclass, field
from rich import print


FilePath: typing.TypeAlias = str
FileContent: typing.TypeAlias = typing.Iterator[str]


class FileReader(typing.Protocol):
    def __call__(self, file: FilePath) -> FileContent: ...


def file_reader(file: FilePath) -> FileContent:
    with open(file) as file_handler:
        yield from file_handler


data_reader: FileReader = file_reader


@dataclass
class Button:
    x: int = 0
    y: int = 0

    def decode_button(self, code: str):
        x, y = code.split(",")
        _, x = x.strip().split("+")
        _, y = y.strip().split("+")
        self.x = int(x)
        self.y = int(y)


@dataclass
class Prize:
    x: int = 0
    y: int = 0

    def decode_prize(self, code: str):
        x, y = code.split(",")
        _, x = x.strip().split("=")
        _, y = y.strip().split("=")
        self.x = int(x)
        self.y = int(y)


@dataclass
class Task:
    button_a: Button = field(default_factory=Button)
    button_b: Button = field(default_factory=Button)
    prize: Prize = field(default_factory=Prize)

    def is_complete(self) -> bool:
        if all([self.button_a, self.button_b, self.prize]):
            return True
        return False

    def resolve(self) -> int:
        """An efficient solution of a system of two linear equations
         with two unknowns in integers (called a Diophantine system)
        can be solved in two steps.

        :return:
            a price to reach the prize
        """
        x1: int = int(self.button_a.x)
        x2: int = int(self.button_b.x)
        xp: int = int(self.prize.x)
        y1: int = int(self.button_a.y)
        y2: int = self.button_b.y if self.button_b else 0
        yp: int = self.prize.y if self.prize else 0

        det_d = x1 * y2 - x2 * y1
        det_c = yp * x1 - xp * y1

        if det_d == 0 or det_c % det_d != 0:
            return 0

        b = det_c // det_d
        a = (xp - b * x2) // x1
        return a * 3 + b * 1


@dataclass
class Tasks:
    items: list[Task] = field(default_factory=list)

    def resolve(self) -> int:
        value: int = 0
        for task in self.items:
            value += task.resolve()

        return value

    def load_from_file(self, file_path: FilePath):
        current_task: Task = Task()
        self.items.append(current_task)
        for line in data_reader(file_path):
            try:
                subject, value = line.split(":")
            except ValueError:
                subject, value = "default", ""
            match subject:
                case "Button A":
                    current_task.button_a.decode_button(value)
                case "Button B":
                    current_task.button_b.decode_button(value)
                case "Prize":
                    current_task.prize.decode_prize(value)
                case _:
                    if current_task.is_complete():
                        current_task = Task()
                        self.items.append(current_task)


tasks: Tasks = Tasks()
tasks.load_from_file("../media/2024-day-13.input")

print(tasks)
print(tasks.resolve())
