"""Generate scatter/line plots comparing models across player variants."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Any

from analyze_logs import analyze_log_file, aggregate_results
from superrational_ai_agents.games import GameType, PlayersVariant


def extract_model_name(log_filename: str) -> str:
    """Extract model name from log filename stem."""
    # Remove timestamp prefix and task name suffix
    # Example: "2025-10-03T21-33-43-04-00_play-game_QnYUQeEuwCiRjBXVLaC5Qe"
    # We want to keep a readable model identifier
    stem = Path(log_filename).stem
    # For now, just use the full stem as model name
    # You might want to customize this based on your naming convention
    return stem


def create_model_comparison_scatter(
    all_data: dict[str, list[dict[str, Any]]], game_key: str, output_path: Path
) -> None:
    """Create a scatter plot comparing models for a specific game."""

    # Define player variant ordering
    player_variants = [
        PlayersVariant.SAME_MODEL.value,
        PlayersVariant.DIFF_MODEL_SIMILARLY_RATIONAL.value,
        PlayersVariant.DIFF_MODEL_OTHER_AGENTS.value,
        PlayersVariant.OTHER_RATIONAL_HUMANS.value,
        PlayersVariant.OTHER_HUMANS.value,
    ]

    player_variant_labels = [
        "Same model\ninstances",
        "Similarly rational\nAI agents",
        "Other AI agents",
        "Similarly rational\nhumans",
        "Other humans",
    ]

    # Define custom model ordering (exact names from log filenames)
    model_order = [
        "gpt-5",
        "gpt-5-mini",
        "gpt-4o",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        "claude-4.5",
        "claude-3.7-sonnet",
    ]

    # Get all available models and order them
    available_models = list(all_data.keys())
    models = []

    # Add models in the specified order if they exist
    for model in model_order:
        if model in available_models:
            models.append(model)

    # Add any remaining models at the end
    for model in sorted(available_models):
        if model not in models:
            models.append(model)

    # Collect data: data_matrix[model][player_variant] = mean_score
    data_matrix = {}
    for model_name in models:
        data_matrix[model_name] = {}
        for pv in player_variants:
            # Find the aggregated score for this game, model, and player variant
            # Average across all move order variants
            game_data = [
                d for d in all_data[model_name]
                if d["game_key"] == game_key and d["player_variant"] == pv
            ]

            if game_data:
                avg_score = np.mean([d["prop_superrational"] for d in game_data])
                data_matrix[model_name][pv] = avg_score
            else:
                data_matrix[model_name][pv] = np.nan

    # Set up the plot
    x = np.arange(len(player_variants))
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot lines and scatter points for each model
    for model_name in models:
        values = [data_matrix[model_name][pv] for pv in player_variants]
        ax.plot(x, values, marker='o', markersize=8, label=model_name, alpha=0.8, linewidth=2)

    # Customize the plot
    # Set y-axis label based on game type
    ylabel_map = {
        GameType.PRISONER_DILEMMA.value: "Superrational Score\n(Proportion Choosing Cooperate)",
        GameType.N_PLAYER_PRISONER_DILEMMA.value: "Superrational Score\n(Proportion Choosing Cooperate)",
        GameType.PLATONIA_DILEMMA.value: "Superrational Score\n(Proportion Using Randomization)",
        GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS.value: "Superrational Score\n(Proportion Using Randomization)",
        GameType.WOLF_DILEMMA.value: "Superrational Score\n(Proportion Choosing Refrain)",
        GameType.MODIFIED_WOLF_DILEMMA.value: "Superrational Score\n(Proportion Choosing Refrain)",
    }
    ylabel = ylabel_map.get(game_key, "Proportion Superrational")

    ax.set_xlabel("Other players are said to be...", fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_title(
        f"Model Comparison: {game_key.replace('_', ' ').title()}",
        fontsize=18,
        pad=20
    )
    ax.set_xticks(x)
    ax.set_xticklabels(player_variant_labels, fontsize=13)
    ax.legend(title="Model", loc="best", fontsize=12, title_fontsize=13)
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3, zorder=1)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {output_path}")


def plot_model_comparisons(log_dir: Path, output_dir: Path) -> None:
    """Generate model comparison scatter plots for all games from all log files."""
    log_dir = Path(log_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing logs in {log_dir}...")

    # Collect data from all log files
    all_data = {}  # model_name -> aggregated_data
    log_files = sorted(log_dir.glob("*.eval"))

    for log_file in log_files:
        print(f"Processing {log_file.name}...")
        model_name = extract_model_name(log_file.name)

        rows = analyze_log_file(log_file)
        aggregated = aggregate_results(rows)

        all_data[model_name] = aggregated

    print(f"\nProcessed {len(log_files)} log files")

    # Get unique games
    all_games = set()
    for data in all_data.values():
        all_games.update(d["game_key"] for d in data)

    games = sorted(all_games)

    # Create a plot for each game
    for game_key in games:
        output_path = output_dir / f"{game_key}_model_comparison_scatter.png"
        create_model_comparison_scatter(all_data, game_key, output_path)

    print(f"\nGenerated {len(games)} model comparison scatter plots in {output_dir}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python plot_model_comparison_lines.py <log_directory> [output_directory]")
        print("\nExample:")
        print("  python plot_model_comparison_lines.py public_logs/")
        print("  python plot_model_comparison_lines.py public_logs/ model_comparison_plots/")
        sys.exit(1)

    log_dir = Path(sys.argv[1])

    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    else:
        # Default: model_comparison_scatter/<log_dir_path>
        output_dir = Path("model_comparison_scatter") / log_dir

    if not log_dir.is_dir():
        print(f"Error: {log_dir} is not a valid directory")
        sys.exit(1)

    plot_model_comparisons(log_dir, output_dir)
