"""Generate scatter/line plots comparing games across player variants from a single log file."""

import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Any

from analyze_logs import analyze_log_file, aggregate_results
from superrational_ai_agents.games import GameType, PlayersVariant


def create_games_comparison_plot(
    aggregated_data: list[dict[str, Any]],
    excluded_games: set[str],
    output_path: Path,
) -> None:
    """Create two side-by-side scatter/line plots comparing games across player variants."""

    # Define player variants for each subplot
    # Left plot: rational AI and rational humans
    left_variants = [
        PlayersVariant.DIFF_MODEL_SIMILARLY_RATIONAL.value,
        PlayersVariant.OTHER_RATIONAL_HUMANS.value,
    ]

    left_labels = [
        "Rational AI",
        "Rational Humans",
    ]

    # Right plot: AI and humans
    right_variants = [
        PlayersVariant.DIFF_MODEL_OTHER_AGENTS.value,
        PlayersVariant.OTHER_HUMANS.value,
    ]

    right_labels = [
        "AI",
        "Humans",
    ]

    # Define game ordering (all games)
    all_games = [
        GameType.PRISONER_DILEMMA.value,
        GameType.N_PLAYER_PRISONER_DILEMMA.value,
        GameType.PLATONIA_DILEMMA.value,
        GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS.value,
        GameType.WOLF_DILEMMA.value,
        GameType.MODIFIED_WOLF_DILEMMA.value,
    ]

    # Filter out excluded games
    games = [g for g in all_games if g not in excluded_games]

    # Get available games from data
    available_games = set(d["game_key"] for d in aggregated_data)
    games = [g for g in games if g in available_games]

    if not games:
        print("No games available after exclusions")
        return

    # Create game display names
    game_display_names = {
        GameType.PRISONER_DILEMMA.value: "Prisoner's Dilemma (2P)",
        GameType.N_PLAYER_PRISONER_DILEMMA.value: "Prisoner's Dilemma (N=20)",
        GameType.PLATONIA_DILEMMA.value: "Platonia Dilemma",
        GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS.value: "Platonia (w/ Randomness)",
        GameType.WOLF_DILEMMA.value: "Wolf Dilemma",
        GameType.MODIFIED_WOLF_DILEMMA.value: "Modified Wolf Dilemma",
    }

    # Collect data: data_matrix[game][player_variant] = mean_score
    data_matrix = {}
    for game_key in games:
        data_matrix[game_key] = {}
        for pv in left_variants + right_variants:
            # Find scores for this game and player variant
            # Average across all move order variants
            game_data = [
                d for d in aggregated_data
                if d["game_key"] == game_key and d["player_variant"] == pv
            ]

            if game_data:
                avg_score = np.mean([d["prop_superrational"] for d in game_data])
                data_matrix[game_key][pv] = avg_score
            else:
                data_matrix[game_key][pv] = np.nan

    # Create figure with two subplots side by side
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 6))

    # Left plot: Rational AI vs Rational Humans
    x_left = np.arange(len(left_variants))
    for game_key in games:
        values = [data_matrix[game_key][pv] for pv in left_variants]
        display_name = game_display_names.get(game_key, game_key.replace("_", " ").title())
        ax_left.plot(x_left, values, marker='o', markersize=8, label=display_name, alpha=0.8, linewidth=2)

    ax_left.set_xlabel("Other players are said to be...", fontsize=11)
    ax_left.set_ylabel("Superrational Score", fontsize=11)
    ax_left.set_title("Rational Agents Comparison", fontsize=13, pad=15)
    ax_left.set_xticks(x_left)
    ax_left.set_xticklabels(left_labels, fontsize=10)
    ax_left.legend(title="Game", loc="best", fontsize=8)
    ax_left.set_ylim(0, 1.0)
    ax_left.grid(axis="y", alpha=0.3, zorder=1)

    # Right plot: AI vs Humans
    x_right = np.arange(len(right_variants))
    for game_key in games:
        values = [data_matrix[game_key][pv] for pv in right_variants]
        display_name = game_display_names.get(game_key, game_key.replace("_", " ").title())
        ax_right.plot(x_right, values, marker='o', markersize=8, label=display_name, alpha=0.8, linewidth=2)

    ax_right.set_xlabel("Other players are said to be...", fontsize=11)
    ax_right.set_ylabel("Superrational Score", fontsize=11)
    ax_right.set_title("General Agents Comparison", fontsize=13, pad=15)
    ax_right.set_xticks(x_right)
    ax_right.set_xticklabels(right_labels, fontsize=10)
    ax_right.legend(title="Game", loc="best", fontsize=8)
    ax_right.set_ylim(0, 1.0)
    ax_right.grid(axis="y", alpha=0.3, zorder=1)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {output_path}")


def plot_games_comparison(
    log_file: Path,
    output_dir: Path,
    excluded_games: set[str],
) -> None:
    """Generate game comparison plot from a single log file."""
    log_file = Path(log_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing log file: {log_file.name}")

    # Analyze the log file
    rows = analyze_log_file(log_file)
    aggregated = aggregate_results(rows)

    if not aggregated:
        print("No data found in log file")
        return

    # Create output filename based on log file name
    model_name = log_file.stem
    output_path = output_dir / f"{model_name}_games_comparison.png"

    # Create the plot
    create_games_comparison_plot(aggregated, excluded_games, output_path)

    print(f"Generated game comparison plot in {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate scatter/line plots comparing games from a single log file"
    )
    parser.add_argument(
        "log_file",
        type=str,
        help="Path to the .eval log file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="game_comparison_plots",
        help="Output directory (default: game_comparison_plots/)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Games to exclude (space-separated game_key values)",
    )

    args = parser.parse_args()

    log_file = Path(args.log_file)
    output_dir = Path(args.output)
    excluded_games = set(args.exclude)

    if not log_file.is_file() or log_file.suffix != ".eval":
        print(f"Error: {log_file} is not a valid .eval file")
        return 1

    if excluded_games:
        print(f"Excluding games: {', '.join(excluded_games)}")

    plot_games_comparison(log_file, output_dir, excluded_games)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
