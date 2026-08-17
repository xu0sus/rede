from random import Random

from redbot.cogs.games.logic import Choice, Result, parse_choice, play_rps, random_opponent


def test_rps_outcomes() -> None:
    assert play_rps(Choice.ROCK, Choice.SCISSORS) is Result.WIN
    assert play_rps(Choice.ROCK, Choice.PAPER) is Result.LOSS
    assert play_rps(Choice.ROCK, Choice.ROCK) is Result.DRAW


def test_parse_choice_and_aliases() -> None:
    assert parse_choice("rock") is Choice.ROCK
    assert parse_choice(" R ") is Choice.ROCK
    assert parse_choice("paper") is Choice.PAPER
    assert parse_choice("invalid") is None


def test_random_opponent_is_deterministic_with_rng() -> None:
    rng = Random(0)
    assert random_opponent(rng) is Choice.PAPER
