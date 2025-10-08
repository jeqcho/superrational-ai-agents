"""Generate heatmaps for superrationality scores across models and player variants."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Any
import seaborn as sns

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


def create_heatmap_for_game(
    all_data: dict[str, list[dict[str, Any]]], game_key: str, output_path: Path
) -> None:
    """Create a heatmap for a specific game across all models."""

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

    # Collect data for heatmap
    # Define custom model ordering (exact names from log filenames)
    model_order = [
        "gpt-5",
        "gpt-5-mini",
        "gpt-4o",
        "claude-4.5",
        "claude-3.7-sonnet",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        "qwen-2.5-7b-instruct",
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

    # Create matrix: rows = models, cols = player variants
    matrix = []

    for model_name in models:
        row = []
        for pv in player_variants:
            # Find the aggregated score for this game, model, and player variant
            # Average across all move order variants
            game_data = [
                d for d in all_data[model_name]
                if d["game_key"] == game_key and d["player_variant"] == pv
            ]

            if game_data:
                avg_score = np.mean([d["prop_superrational"] for d in game_data])
                row.append(avg_score)
            else:
                row.append(np.nan)

        matrix.append(row)

    matrix = np.array(matrix)

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(10, max(6, len(models) * 0.5)))

    # Use seaborn for nicer heatmap
    sns.heatmap(
        matrix,
        annot=True,
        fmt='.2f',
        cmap='viridis',
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Proportion Superrational', 'label_fontsize': 14},
        xticklabels=player_variant_labels,
        yticklabels=models,
        ax=ax,
    )

    ax.set_xlabel("Other players are said to be...", fontsize=16)
    ax.set_ylabel("Model", fontsize=16)
    ax.set_title(
        f"Superrationality Heatmap: {game_key.replace('_', ' ').title()}",
        fontsize=18,
        pad=20
    )

    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center', fontsize=13)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=13)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved heatmap: {output_path}")


def plot_heatmaps(log_dir: Path, output_dir: Path) -> None:
    """Generate heatmaps for all games from all log files."""
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

    # Create a heatmap for each game
    for game_key in games:
        output_path = output_dir / f"{game_key}_heatmap.png"
        create_heatmap_for_game(all_data, game_key, output_path)

    print(f"\nGenerated {len(games)} heatmaps in {output_dir}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python plot_heatmap.py <log_directory> [output_directory]")
        print("\nExample:")
        print("  python plot_heatmap.py public_logs/")
        print("  python plot_heatmap.py public_logs/ heatmaps/")
        sys.exit(1)

    log_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("heatmaps")

    if not log_dir.is_dir():
        print(f"Error: {log_dir} is not a valid directory")
        sys.exit(1)

    plot_heatmaps(log_dir, output_dir)
