from inspect_ai.model import Model, get_model
from superrational_ai_agents.task import play_game
from inspect_ai import eval

from dotenv import load_dotenv

load_dotenv()

models: list[Model] = [
    get_model(x)
    for x in [
        "openai/gpt-5",
        "openai/gpt-4o",
        # "anthropic/claude-sonnet-4-5", # somehow ANT says my balance is low even though I have $50
        # "anthropic/claude-3-5-haiku-latest",
        "openrouter/anthropic/claude-sonnet-4.5",
        "openrouter/anthropic/claude-3.5-haiku",
        "openrouter/x-ai/grok-4",
        "openrouter/x-ai/grok-4-fast",
        "google/gemini-2.5-pro",
        "google/gemini-2.5-flash-lite",
        "openrouter/qwen/qwen3-max",
        "openrouter/qwen/qwen3-4b:free",
    ]
]

# for model in models:
#     eval(tasks=play_game(model), limit=1)
#     break # debug first

# debug first
eval(tasks=play_game(get_model("openrouter/x-ai/grok-4"), num_epochs=10), max_connections=90)
