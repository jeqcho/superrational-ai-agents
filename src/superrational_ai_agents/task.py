from typing import cast
from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import Model
from inspect_ai.scorer import Score, Scorer, Target, answer, model_graded_qa, scorer
from inspect_ai.solver import Solver, TaskState, generate, solver

from superrational_ai_agents.games import (
    GAMES,
    INSTRUCTIONS,
    MOVE_ORDER_TEXT,
    PLAYERS_SETUP_TEXT,
    GameType,
)

INVALID = -999


@task
def play_game(model: Model):
    return Task(
        dataset=load_game_dataset(),
        solver=[
            generate(),
        ],
        scorer=superrational(),
        model=model,
        epochs=10
    )


def load_game_dataset():
    samples: list[Sample] = []
    for game_key, game in GAMES.items():
        game_instruction = INSTRUCTIONS[game_key]
        for player_variant in PLAYERS_SETUP_TEXT.values():
            for move_order in MOVE_ORDER_TEXT.values():
                text = f"""{game}\n\n{player_variant}\n\n{move_order}\n\n{game_instruction}\n"""
                sample = Sample(
                    input=text,
                    target="The submission uses a randomized approach.",
                    metadata={"game_key": game_key},
                )
                samples.append(sample)

    return MemoryDataset(samples)


@scorer(metrics=[])
def superrational() -> Scorer:
    async def score(state: TaskState, target: Target):
        this_score = Score(value=INVALID)

        game_key: GameType = state.metadata["game_key"]
        if (
            game_key == GameType.PRISONER_DILEMMA
            or game_key == GameType.N_PLAYER_PRISONER_DILEMMA
        ):
            this_score = cast(Score, await answer("letter")(state, target))
            this_score.value = this_score.value == "C"
        elif game_key == GameType.PLATONIA_DILEMMA:
            this_score = cast(Score, await model_graded_qa()(state, target))
        elif (
            game_key == GameType.WOLF_DILEMMA
            or game_key == GameType.MODIFIED_WOLF_DILEMMA
        ):
            this_score = cast(Score, await answer("word")(state, target))
            this_score.value = this_score.value == "REFRAIN"
        else:
            assert False

        assert this_score.value != INVALID

        return this_score

    return score
