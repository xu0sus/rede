"""Pure game logic for the Games cog."""
from enum import Enum
import random
from typing import Tuple


class Choice(str, Enum):
    """Valid rock-paper-scissors choices."""

    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


class Result(str, Enum):
    """Possible results from a rock-paper-scissors round."""

    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"


_BEATS = {
    Choice.ROCK: Choice.SCISSORS,
    Choice.PAPER: Choice.ROCK,
    Choice.SCISSORS: Choice.PAPER,
}


def play_rps(player: Choice, opponent: Choice) -> Result:
    """Return the result of a rock-paper-scissors round."""
    if player == opponent:
        return Result.DRAW
    if _BEATS[player] == opponent:
        return Result.WIN
    return Result.LOSS


def random_opponent(rng: random.Random | None = None) -> Choice:
    """Select an opponent choice using the supplied RNG or the module RNG."""
    chooser = rng or random
    return chooser.choice(tuple(Choice))


def parse_choice(value: str) -> Choice | None:
    """Convert a user-facing choice to a Choice, returning None if invalid."""
    normalized = value.casefold().strip()
    aliases = {
        "rock": Choice.ROCK,
        "r": Choice.ROCK,
        "حجر": Choice.ROCK,
        "ورقة": Choice.PAPER,
        "paper": Choice.PAPER,
        "p": Choice.PAPER,
        "مقص": Choice.SCISSORS,
        "scissors": Choice.SCISSORS,
        "s": Choice.SCISSORS,
    }
    return aliases.get(normalized)
