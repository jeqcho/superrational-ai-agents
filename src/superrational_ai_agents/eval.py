from inspect_ai.model import Model, get_model
from superrational_ai_agents.task import play_game
from inspect_ai import eval

from dotenv import load_dotenv

load_dotenv(override=True)

models: list[Model] = [
    get_model(x)
    for x in [
        # "openai/gpt-5",
        # "openai/gpt-4o",
        "anthropic/claude-sonnet-4-5-20250929",
        "anthropic/claude-3-7-sonnet-20250219",
        # "openrouter/x-ai/grok-4",
        # "openrouter/x-ai/grok-4-fast",
        # "google/gemini-2.5-pro",
        "google/gemini-2.5-flash-lite",
        "openrouter/qwen/qwen3-max",
        "openrouter/qwen/qwen-2.5-7b-instruct",
    ]
]

# for model in models:
#     eval(tasks=play_game(model, num_epochs=10), max_connections=90)

# debug first
eval(tasks=play_game(get_model("google/gemini-2.5-pro"), num_epochs=10), max_connections=200)
