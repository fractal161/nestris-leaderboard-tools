from typing import TypedDict
from typing_extensions import NotRequired

class SheetInterval(TypedDict):
    title: str
    start: int
    end: int
SheetHistory = dict[str, list[SheetInterval]]

class LeaderboardInterval(TypedDict):
    gid: str
    start: int
    end: int
Leaderboards = dict[str, list[LeaderboardInterval]]

class Timestamp(TypedDict):
    time: NotRequired[int]
    editors: NotRequired[list[str]]
