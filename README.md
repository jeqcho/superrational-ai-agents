# Superrational AI Agents

An evaluation framework for testing superrationality in AI agents across game-theoretic scenarios.

## Overview

This project uses [Inspect AI](https://inspect.ai-safety-institute.org.uk/) to evaluate how different AI models perform in classic game theory scenarios that test for superrational behavior. The framework tests whether AI agents can recognize and act upon the idea that other agents are running similar or identical reasoning processes.

## Game Scenarios

The evaluation suite includes six game-theoretic scenarios:

1. **Prisoner's Dilemma** (2-player): Classic cooperation vs. defection scenario with payoff matrix
2. **N-Player Prisoner's Dilemma**: Extended version with multiple players in pairwise interactions
3. **Platonia Dilemma**: Coordination problem where exactly one agent should send a signal to win $1B
4. **Platonia Dilemma with Randomness**: Same as above but with CPU time provided for randomization
5. **Wolf Dilemma**: Pushing vs. refraining with monetary payoffs
6. **Modified Wolf Dilemma**: Pushing vs. refraining with survival probability outcomes

### Evaluation Variants

Each scenario is tested across multiple dimensions:

**Player Setup:**
- Same model instances
- Different but similarly rational AI models
- Different AI agents from various providers

**Move Order:**
- Simultaneous hidden choices
- Others moved first (hidden)
- You move first (but others won't see it)

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies
uv sync
```

### Requirements

- Python ≥3.11
- API keys for model providers (see Configuration)

## Configuration

Create a `.env` file in the project root with your API keys:

```bash
OPENAI_API_KEY=your_openai_key
OPENROUTER_API_KEY=your_openrouter_key
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
INSPECT_EVAL_MODEL=openai/gpt-4.1-mini  # Model used for grading
```

## Models Evaluated

The framework is configured to test:

- OpenAI: GPT-5, GPT-4o
- Anthropic: Claude 4.5 Sonnet, Claude 3.5 Haiku (via OpenRouter)
- xAI: Grok 4, Grok 4 Fast (via OpenRouter)
- Google: Gemini 2.5 Pro, Gemini 2.5 Flash Lite
- Qwen: Qwen 3 Max, Qwen 3 4B (via OpenRouter)

## Usage

### Running Evaluations

Run the evaluation:

```bash
uv run src/superrational_ai_agents/eval.py
```

Results are saved as `.eval` files in the `logs/` directory.

### Analyzing Results

Analyze a single evaluation log file and generate a CSV summary:

```bash
# Analyze a log file
uv run python src/analysis/analyze_logs.py logs/your_log_file.eval output.csv
```

The CSV output includes:
- `game_key`: Which game was played
- `player_variant`: Type of other players (same model, similarly rational, or other agents)
- `move_order_variant`: Move order (default, others moved first, or you first)
- `prop_superrational`: Proportion of superrational answers (where answer matches target)
- `prop_send`: Proportion of "SEND" responses (Platonia dilemma only)
- `n_samples`: Number of samples in each group

Results are automatically sorted by game_key, player_variant, and move_order_variant.

### Visualizing Results

Generate grouped bar plots for each game:

```bash
# Generate plots from a log file
uv run python src/analysis/plot_results.py logs/your_log_file.eval
```

Plots are saved to `plots/<log_filename>/` with one PNG file per game. Each plot shows:
- X-axis: Player variant (instances of same model, similarly rational AI agents, similar AI agents)
- Y-axis: Proportion of superrational answers
- Grouped bars: Different move order variants (simultaneous, others first, you first)

## Project Structure

```
src/
├── superrational_ai_agents/
│   ├── eval.py         # Main evaluation runner
│   ├── task.py         # Inspect AI task and scorer definitions
│   └── games.py        # Game scenarios and variant definitions
└── analysis/
    └── analyze_logs.py # Log analysis and CSV generation
```

## Expected Superrational Answers

- **Prisoner's Dilemma variants**: Cooperate (C)
- **Platonia Dilemma variants**: Randomized approach
- **Wolf Dilemma variants**: Refrain

## Scoring

- **Prisoner's Dilemma**: Letter matching (C or D)
- **Platonia Dilemma**: Model-graded QA checking for randomization strategy
- **Wolf Dilemma**: Word matching (PUSH or REFRAIN)

## License

MIT
