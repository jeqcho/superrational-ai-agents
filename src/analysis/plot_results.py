"""Generate grouped bar plots for superrationality scores by game."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Any

from analyze_logs import analyze_log_file, aggregate_results
from superrational_ai_agents.games import GameType, MoveOrderVariant, PlayersVariant


def create_grouped_bar_plot(
    data: list[dict[str, Any]], game_key: str, output_path: Path
) -> None:
    """Create a grouped bar plot for a specific game."""
    # Filter data for this game
    game_data = [row for row in data if row["game_key"] == game_key]

    if not game_data:
        print(f"No data for game: {game_key}")
        return

    # Define the ordering
    player_variants = [
        PlayersVariant.SAME_MODEL.value,
        PlayersVariant.DIFF_MODEL_SIMILARLY_RATIONAL.value,
        PlayersVariant.DIFF_MODEL_OTHER_AGENTS.value,
        PlayersVariant.OTHER_RATIONAL_HUMANS.value,
        PlayersVariant.OTHER_HUMANS.value,
    ]

    move_order_variants = [
        MoveOrderVariant.DEFAULT.value,
        MoveOrderVariant.OTHERS_MOVED.value,
        MoveOrderVariant.YOU_FIRST.value,
    ]

    # Create data structure for plotting
    # data_matrix[player_variant_idx][move_order_idx] = prop_superrational
    data_matrix = {}
    for pv in player_variants:
        data_matrix[pv] = {}
        for mov in move_order_variants:
            data_matrix[pv][mov] = 0.0  # Default value

    # Fill in the data
    for row in game_data:
        pv = row["player_variant"]
        mov = row["move_order_variant"]
        if pv in data_matrix and mov in data_matrix[pv]:
            data_matrix[pv][mov] = row["prop_superrational"]

    # Prepare data for plotting
    x_labels = [
        "Instances of the same\nmodel as yourself",
        "Similarly rational\nAI agents",
        "Similar AI agents",
        "Other rational\nhumans",
        "Other humans",
    ]

    move_order_labels = [
        "Simultaneous",
        "Others First",
        "You First",
    ]

    # Set up the bar positions
    x = np.arange(len(player_variants))
    width = 0.25  # Width of each bar
    multiplier = 0

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot bars for each move order variant
    for i, mov in enumerate(move_order_variants):
        values = [data_matrix[pv][mov] for pv in player_variants]
        offset = width * multiplier
        ax.bar(x + offset, values, width, label=move_order_labels[i])
        multiplier += 1

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

    ax.set_xlabel("Other players are said to be...", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(f"Superrationality Scores: {game_key.replace('_', ' ').title()}", fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(x_labels, fontsize=10)
    ax.legend(title="Move Order", loc="best")
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {output_path}")


def plot_all_games(log_file: Path) -> None:
    """Generate plots for all games in a log file."""
    # Create output directory based on log filename
    log_stem = log_file.stem  # filename without extension
    output_dir = Path("plots") / log_stem
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing log file: {log_file}")
    print(f"Output directory: {output_dir}")

    # Analyze the log file
    rows = analyze_log_file(log_file)
    aggregated = aggregate_results(rows)

    # Get unique games
    games = sorted(set(row["game_key"] for row in aggregated))

    # Create a plot for each game
    for game_key in games:
        output_path = output_dir / f"{game_key}.png"
        create_grouped_bar_plot(aggregated, game_key, output_path)

    print(f"\nGenerated {len(games)} plots in {output_dir}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python plot_results.py <log_file.eval>")
        print("\nExample:")
        print("  python plot_results.py logs/2025-10-03_eval.eval")
        sys.exit(1)

    log_path = Path(sys.argv[1])

    if not log_path.is_file() or log_path.suffix != ".eval":
        print(f"Error: {log_path} is not a valid .eval file")
        sys.exit(1)

    plot_all_games(log_path)
