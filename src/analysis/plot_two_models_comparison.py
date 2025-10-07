"""Generate scatter/line plots comparing two models across all games for 'same model' player variant."""

import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Any

from analyze_logs import analyze_log_file, aggregate_results
from superrational_ai_agents.games import GameType, PlayersVariant


def create_two_models_comparison_plot(
    data1: list[dict[str, Any]],
    data2: list[dict[str, Any]],
    model1_name: str,
    model2_name: str,
    output_path: Path,
) -> None:
    """Create a scatter/line plot comparing two models across all games."""

    # Only use "same model" player variant
    player_variant = PlayersVariant.SAME_MODEL.value

    # Define game ordering (all games)
    all_games = [
        GameType.PRISONER_DILEMMA.value,
        GameType.N_PLAYER_PRISONER_DILEMMA.value,
        GameType.PLATONIA_DILEMMA.value,
        GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS.value,
        GameType.WOLF_DILEMMA.value,
        GameType.MODIFIED_WOLF_DILEMMA.value,
    ]

    # Create game display names
    game_display_names = {
        GameType.PRISONER_DILEMMA.value: "Prisoner's Dilemma (2P)",
        GameType.N_PLAYER_PRISONER_DILEMMA.value: "Prisoner's Dilemma (N=20)",
        GameType.PLATONIA_DILEMMA.value: "Platonia Dilemma",
        GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS.value: "Platonia (w/ Randomness)",
        GameType.WOLF_DILEMMA.value: "Wolf Dilemma",
        GameType.MODIFIED_WOLF_DILEMMA.value: "Modified Wolf Dilemma",
    }

    # Collect data for model 1
    model1_scores = {}
    for game_key in all_games:
        game_data = [
            d for d in data1
            if d["game_key"] == game_key and d["player_variant"] == player_variant
        ]
        if game_data:
            avg_score = np.mean([d["prop_superrational"] for d in game_data])
            model1_scores[game_key] = avg_score
        else:
            model1_scores[game_key] = np.nan

    # Collect data for model 2
    model2_scores = {}
    for game_key in all_games:
        game_data = [
            d for d in data2
            if d["game_key"] == game_key and d["player_variant"] == player_variant
        ]
        if game_data:
            avg_score = np.mean([d["prop_superrational"] for d in game_data])
            model2_scores[game_key] = avg_score
        else:
            model2_scores[game_key] = np.nan

    # Filter games that have data in at least one model
    games = [
        g for g in all_games
        if not (np.isnan(model1_scores.get(g, np.nan)) and np.isnan(model2_scores.get(g, np.nan)))
    ]

    if not games:
        print("No games available with data")
        return

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))

    # X-axis positions: 0 for model1, 1 for model2
    x = np.array([0, 1])
    x_labels = [model1_name, model2_name]

    # Plot each game as a line connecting the two models
    for game_key in games:
        values = [model1_scores[game_key], model2_scores[game_key]]
        display_name = game_display_names.get(game_key, game_key.replace("_", " ").title())

        # Plot line connecting the two points
        ax.plot(x, values, marker='o', markersize=10, label=display_name, alpha=0.8, linewidth=2)

    # Customize the plot
    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Superrational Score", fontsize=12)
    ax.set_title("Model Comparison Across Games\n(Instances of Same Model)", fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=11)
    ax.legend(title="Game", loc="best", fontsize=9)
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3, zorder=1)
    ax.set_xlim(-0.2, 1.2)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {output_path}")


def plot_two_models_comparison(
    log_file1: Path,
    log_file2: Path,
    output_dir: Path,
) -> None:
    """Generate comparison plot from two log files."""
    log_file1 = Path(log_file1)
    log_file2 = Path(log_file2)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing log file 1: {log_file1.name}")
    rows1 = analyze_log_file(log_file1)
    aggregated1 = aggregate_results(rows1)

    print(f"Analyzing log file 2: {log_file2.name}")
    rows2 = analyze_log_file(log_file2)
    aggregated2 = aggregate_results(rows2)

    if not aggregated1 or not aggregated2:
        print("No data found in one or both log files")
        return

    # Extract model names from filenames
    model1_name = log_file1.stem
    model2_name = log_file2.stem

    # Create output filename
    output_path = output_dir / f"{model1_name}_vs_{model2_name}_comparison.png"

    # Create the plot
    create_two_models_comparison_plot(
        aggregated1, aggregated2, model1_name, model2_name, output_path
    )

    print(f"Generated comparison plot in {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate scatter/line plot comparing two models across all games"
    )
    parser.add_argument(
        "log_file1",
        type=str,
        help="Path to the first .eval log file",
    )
    parser.add_argument(
        "log_file2",
        type=str,
        help="Path to the second .eval log file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="two_models_comparison_plots",
        help="Output directory (default: two_models_comparison_plots/)",
    )

    args = parser.parse_args()

    log_file1 = Path(args.log_file1)
    log_file2 = Path(args.log_file2)
    output_dir = Path(args.output)

    if not log_file1.is_file() or log_file1.suffix != ".eval":
        print(f"Error: {log_file1} is not a valid .eval file")
        return 1

    if not log_file2.is_file() or log_file2.suffix != ".eval":
        print(f"Error: {log_file2} is not a valid .eval file")
        return 1

    plot_two_models_comparison(log_file1, log_file2, output_dir)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
