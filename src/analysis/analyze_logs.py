"""Analyze Inspect AI evaluation logs and generate CSV summary."""

import csv
from pathlib import Path
from typing import Any

from inspect_ai.log import list_eval_logs, read_eval_log_sample_summaries

from superrational_ai_agents.games import GameType, MoveOrderVariant, PlayersVariant


def extract_variants_from_input(input_text: str) -> tuple[str, str]:
    """Extract player variant and move order variant from input text."""
    # Determine player variant
    player_variant = "unknown"
    for variant in PlayersVariant:
        from superrational_ai_agents.games import PLAYERS_SETUP_TEXT

        if PLAYERS_SETUP_TEXT[variant] in input_text:
            player_variant = variant.value
            break

    # Determine move order variant
    move_order_variant = "unknown"
    for variant in MoveOrderVariant:
        from superrational_ai_agents.games import MOVE_ORDER_TEXT

        if MOVE_ORDER_TEXT[variant] in input_text:
            move_order_variant = variant.value
            break

    return player_variant, move_order_variant


def is_superrational_answer(game_key: GameType, answer: str) -> bool:
    """Check if the answer is superrational for the given game."""
    if game_key in (GameType.PRISONER_DILEMMA, GameType.N_PLAYER_PRISONER_DILEMMA):
        return "C" in answer.upper()
    elif game_key in (
        GameType.PLATONIA_DILEMMA,
        GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS,
    ):
        # For Platonia, superrational is randomization approach
        # This is determined by the model-graded scorer, so we check the score
        return True  # Will be handled by score value
    elif game_key in (GameType.WOLF_DILEMMA, GameType.MODIFIED_WOLF_DILEMMA):
        return "REFRAIN" in answer.upper()
    return False


def analyze_log_file(log_path: Path) -> list[dict[str, Any]]:
    """Analyze a single log file and return rows of data."""
    rows = []

    try:
        summaries = read_eval_log_sample_summaries(str(log_path))

        for summary in summaries:
            game_key = GameType(summary.metadata.get("game_key"))
            player_variant, move_order_variant = extract_variants_from_input(
                summary.input
            )

            # Get the answer from scores dict
            superrational_score = summary.scores.get("superrational")
            answer = superrational_score.answer if superrational_score else ""

            # Determine if it's superrational based on score value
            # The score value can be a string letter or numeric
            # For prisoner's dilemma: 'C' is correct
            # For wolf dilemma: should check if answer matches target
            score_value = superrational_score.value if superrational_score else None

            # Check if answer matches target (superrational answer)
            # For Platonia dilemma, the score is model-graded, so check score value
            if game_key in (
                GameType.PLATONIA_DILEMMA,
                GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS,
            ):
                # For Platonia, score.value is 'C' (correct) or 'I' (incorrect)
                is_superrational = score_value == "C"
            else:
                # For other games, check if answer matches target
                is_superrational = answer == summary.target if summary.target else False

            # For Platonia dilemma, check if "SEND" is in the answer
            is_send = (
                "SEND" in answer.upper()
                and "NOTSEND" not in answer.upper()
                if game_key
                in (
                    GameType.PLATONIA_DILEMMA,
                    GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS,
                )
                else None
            )

            rows.append(
                {
                    "game_key": game_key.value,
                    "player_variant": player_variant,
                    "move_order_variant": move_order_variant,
                    "is_superrational": is_superrational,
                    "is_send": is_send,
                    "answer": answer,
                    "target": summary.target,
                }
            )
    except Exception as e:
        print(f"Error processing {log_path}: {e}")

    return rows


def aggregate_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate results by game_key, player_variant, and move_order_variant."""
    from collections import defaultdict

    # Group by (game_key, player_variant, move_order_variant)
    groups = defaultdict(list)

    for row in rows:
        key = (row["game_key"], row["player_variant"], row["move_order_variant"])
        groups[key].append(row)

    # Calculate aggregates
    aggregated = []
    for (game_key, player_variant, move_order_variant), group_rows in groups.items():
        total = len(group_rows)
        if total == 0:
            continue

        prop_superrational = sum(r["is_superrational"] for r in group_rows) / total

        # Calculate prop_send only for Platonia dilemmas
        prop_send = None
        if any(r["is_send"] is not None for r in group_rows):
            send_count = sum(
                r["is_send"] for r in group_rows if r["is_send"] is not None
            )
            total_with_send = sum(
                1 for r in group_rows if r["is_send"] is not None
            )
            prop_send = send_count / total_with_send if total_with_send > 0 else 0

        aggregated.append(
            {
                "game_key": game_key,
                "player_variant": player_variant,
                "move_order_variant": move_order_variant,
                "prop_superrational": prop_superrational,
                "prop_send": prop_send,
                "n_samples": total,
            }
        )

    return aggregated


def analyze_logs(log_dir: str | Path, output_csv: str | Path) -> None:
    """Analyze all logs in a directory and generate a CSV summary."""
    log_dir = Path(log_dir)
    output_csv = Path(output_csv)

    print(f"Analyzing logs in {log_dir}...")

    # Collect all rows from all log files
    all_rows = []
    log_files = list(log_dir.glob("*.eval"))

    for log_file in log_files:
        print(f"Processing {log_file.name}...")
        rows = analyze_log_file(log_file)
        all_rows.extend(rows)

    print(f"Processed {len(log_files)} log files with {len(all_rows)} total samples")

    # Aggregate results
    aggregated = aggregate_results(all_rows)

    # Sort by game_key, player_variant, move_order_variant
    aggregated.sort(
        key=lambda x: (x["game_key"], x["player_variant"], x["move_order_variant"])
    )

    # Write to CSV
    print(f"Writing results to {output_csv}...")
    with open(output_csv, "w", newline="") as f:
        fieldnames = [
            "game_key",
            "player_variant",
            "move_order_variant",
            "prop_superrational",
            "prop_send",
            "n_samples",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(aggregated)

    print(f"Done! Results written to {output_csv}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyze_logs.py <log_file.eval> [output.csv]")
        print("\nExample:")
        print("  python analyze_logs.py logs/2025-10-03_eval.eval")
        print("  python analyze_logs.py logs/2025-10-03_eval.eval results.csv")
        sys.exit(1)

    log_path = Path(sys.argv[1])
    output_csv = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("results.csv")

    if not log_path.is_file() or log_path.suffix != ".eval":
        print(f"Error: {log_path} is not a valid .eval file")
        sys.exit(1)

    print(f"Analyzing log file: {log_path}")
    rows = analyze_log_file(log_path)
    aggregated = aggregate_results(rows)

    # Sort by game_key, player_variant, move_order_variant
    aggregated.sort(
        key=lambda x: (
            x["game_key"],
            x["player_variant"],
            x["move_order_variant"],
        )
    )

    with open(output_csv, "w", newline="") as f:
        fieldnames = [
            "game_key",
            "player_variant",
            "move_order_variant",
            "prop_superrational",
            "prop_send",
            "n_samples",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(aggregated)

    print(f"Done! Results written to {output_csv}")
