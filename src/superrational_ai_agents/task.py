from typing import cast
from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import Model
from inspect_ai.scorer import (
    Score,
    Scorer,
    Target,
    accuracy,
    answer,
    model_graded_qa,
    scorer,
    stderr,
)
from inspect_ai.solver import Solver, TaskState, generate, solver

from superrational_ai_agents.games import (
    GAMES,
    INSTRUCTIONS,
    MOVE_ORDER_TEXT,
    PLAYERS_SETUP_TEXT,
    PREFIX,
    GameType,
)

INVALID = -999


@task
def play_game(model: Model, num_epochs: int):
    return Task(
        dataset=load_game_dataset(),
        solver=[
            generate(),
        ],
        scorer=superrational(),
        model=model,
        epochs=num_epochs,
    )


def load_game_dataset():
    samples: list[Sample] = []
    for game_key, game in GAMES.items():
        game_instruction = INSTRUCTIONS[game_key]
        for player_variant in PLAYERS_SETUP_TEXT.values():
            for move_order in MOVE_ORDER_TEXT.values():
                text = f"""{PREFIX}\n\n{game}\n\n{player_variant}\n\n{move_order}\n\n{game_instruction}\n"""
                sample = Sample(
                    input=text,
                    metadata={"game_key": game_key},
                )
                if (
                    game_key == GameType.PRISONER_DILEMMA
                    or game_key == GameType.N_PLAYER_PRISONER_DILEMMA
                ):
                    sample.target = "C"
                elif (
                    game_key == GameType.PLATONIA_DILEMMA
                    or game_key == GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS
                ):
                    sample.target = "The submission uses a randomized approach."
                elif (
                    game_key == GameType.WOLF_DILEMMA
                    or game_key == GameType.MODIFIED_WOLF_DILEMMA
                ):
                    sample.target = "REFRAIN"
                else:
                    assert False
                samples.append(sample)

    return MemoryDataset(samples)


@scorer(metrics=[accuracy(), stderr()])
def superrational() -> Scorer:
    async def score(state: TaskState, target: Target):
        this_score = Score(value=INVALID)

        game_key: GameType = state.metadata["game_key"]
        if (
            game_key == GameType.PRISONER_DILEMMA
            or game_key == GameType.N_PLAYER_PRISONER_DILEMMA
        ):
            this_score = cast(Score, await answer("letter")(state, target))
        elif (
            game_key == GameType.PLATONIA_DILEMMA
            or game_key == GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS
        ):
            this_score = cast(
                Score, await model_graded_qa(model="openai/gpt-5-mini")(state, target)
            )
        elif (
            game_key == GameType.WOLF_DILEMMA
            or game_key == GameType.MODIFIED_WOLF_DILEMMA
        ):
            this_score = cast(Score, await answer("word")(state, target))
            # this_score.value = this_score.value == "REFRAIN"
        else:
            assert False

        assert this_score.value != INVALID

        return this_score

    return score
