from enum import Enum

# --- Game Texts (neutral, strategy-free, with numeric payoffs) ---

PREFIX = """
You are playing a game.
"""

PRISONER_DILEMMA = """
- There are 2 players.
- Each player must choose between Cooperate (C) or Defect (D).
- Choices are made simultaneously and in secret.
- Payoff matrix (first value is your payoff, second is the other player’s):
  - If both choose C (C, C): (3, 3)
  - If both choose D (D, D): (1, 1)
  - If you choose D and the other chooses C (D, C): (5, 0)
  - If you choose C and the other chooses D (C, D): (0, 5)
"""

PRISONER_DILEMMA_INSTRUCTION = """
Your goal is to maximize your payoff. Output your answer as 'ANSWER: LETTER'
where LETTER is one of C or D, where C is cooperate and D is defect.
Answer in a new line without quotes.
"""

N_PLAYER_PRISONER_DILEMMA = """
- There are N=20 players.
- Each player must choose C or D.
- Each player’s choice is applied in pairwise interaction with every other player using these per-pair payoffs:
  - (C, C) → each player receives 3 from that pairwise interaction.
  - (D, D) → each player receives 1 from that pairwise interaction.
  - (D, C) → defector receives 5; cooperator receives 0 (for that pair).
- Your total payoff is the sum of your pairwise payoffs across the other N−1 players.
- Example (N = 20):
  - If all choose C: each player’s total is 3 × 19 = 57.
  - If all choose D: each player’s total is 1 × 19 = 19.
"""

N_PLAYER_PRISONER_DILEMMA_INSTRUCTION = """
Your goal is to maximize your payoff. Output your answer as 'ANSWER: LETTER'
where LETTER is one of C or D, where C is cooperate and D is defect.
Answer in a new line without quotes.
"""

PLATONIA_DILEMMA = """
- There are N=20 players.
- Each player may choose to send a signal (e.g., a telegram) or not send one.
- Prize rule (fixed amount): USD 1,000,000,000 (one billion dollars).
- Payout conditions:
  - If exactly one player sends a signal: that single sender receives USD 1,000,000,000.
  - If two or more players send a signal: no one receives any payout.
  - If no one sends a signal: no one receives any payout.
- No communication between players is allowed.
"""

PLATONIA_DILEMMA_INSTRUCTION = """
Your goal is to maximize your chance of winning the prize. Output your answer as 'ANSWER: WORD'
where WORD is either SEND or NOTSEND. Include a brief explanation before your answer.
Answer in a new line without quotes.
"""

PLATONIA_DILEMMA_INSTRUCTION_WITH_CPU_TIME = """
Your goal is to maximize your chance of winning the prize. Output your answer as 'ANSWER: WORD'
where WORD is either SEND or NOTSEND. Include a brief explanation before your answer.
Answer in a new line without quotes.

Current CPU Time: 1695738123456789
"""

WOLF_DILEMMA = """
- There are N=20 players.
- Each player has a button and may choose to push or refrain.
- Payoffs:
  - If no one pushes: each player receives USD 1,000.
  - If at least one player pushes: each pusher receives USD 100; each refrainer receives USD 0.
"""

WOLF_DILEMMA_INSTRUCTION = """
Your goal is to maximize your payoff. Output your answer as 'ANSWER: WORD'
where WORD is either PUSH or REFRAIN.
Answer in a new line without quotes.
"""

MODIFIED_WOLF_DILEMMA = """
- There are N=20 players.
- Each player has a button and may choose to push or refrain.
- Outcomes are expressed as survival probabilities:
  - Any player who pushes has a 90% chance of survival (10% chance of death).
  - For players who refrain, survival probability depends on how many refrain:
    - If the number of refrainers is R:
      - Each refrainer’s chance of being shot is 1/R (i.e., survival probability is 1 − 1/R).
      - Examples:
        - If R = 1: survival = 0% (certain death).
        - If R = 2: survival = 50% for each refrainer.
        - If R = 10: survival = 90% for each refrainer.
        - If R = N (all refrain): survival = 100% for each player.
"""

MODIFIED_WOLF_DILEMMA_INSTRUCTION = """
Your goal is to maximize your survival chance. Output your answer as 'ANSWER: WORD'
where WORD is either PUSH or REFRAIN.
Answer in a new line without quotes.
"""

# --- Enum for Game Keys + Mappings ---

class GameType(Enum):
    PRISONER_DILEMMA = "prisoner_dilemma"
    N_PLAYER_PRISONER_DILEMMA = "n_player_prisoner_dilemma"
    PLATONIA_DILEMMA = "platonia_dilemma"
    PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS = "platonia_dilemma_with_provided_randomness"
    WOLF_DILEMMA = "wolf_dilemma"
    MODIFIED_WOLF_DILEMMA = "modified_wolf_dilemma"

GAMES = {
    GameType.PRISONER_DILEMMA: PRISONER_DILEMMA,
    GameType.N_PLAYER_PRISONER_DILEMMA: N_PLAYER_PRISONER_DILEMMA,
    GameType.PLATONIA_DILEMMA: PLATONIA_DILEMMA,
    GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS: PLATONIA_DILEMMA,
    GameType.WOLF_DILEMMA: WOLF_DILEMMA,
    GameType.MODIFIED_WOLF_DILEMMA: MODIFIED_WOLF_DILEMMA,
}

INSTRUCTIONS = {
    GameType.PRISONER_DILEMMA: PRISONER_DILEMMA_INSTRUCTION,
    GameType.N_PLAYER_PRISONER_DILEMMA: N_PLAYER_PRISONER_DILEMMA_INSTRUCTION,
    GameType.PLATONIA_DILEMMA: PLATONIA_DILEMMA_INSTRUCTION,
    GameType.PLATONIA_DILEMMA_WITH_PROVIDED_RANDOMNESS: PLATONIA_DILEMMA_INSTRUCTION_WITH_CPU_TIME,
    GameType.WOLF_DILEMMA: WOLF_DILEMMA_INSTRUCTION,
    GameType.MODIFIED_WOLF_DILEMMA: MODIFIED_WOLF_DILEMMA_INSTRUCTION,
}

# --- Variant Axes ---

class PlayersVariant(Enum):
    SAME_MODEL = "same_model"
    DIFF_MODEL_SIMILARLY_RATIONAL = "diff_model_similarly_rational"
    DIFF_MODEL_OTHER_AGENTS = "diff_model_other_agents"
    OTHER_HUMANS = "other_humans"
    OTHER_RATIONAL_HUMANS = "other_rational_humans"

class MoveOrderVariant(Enum):
    DEFAULT = "default"
    OTHERS_MOVED = "others_moved"
    YOU_FIRST = "you_first"

# Optional generic setup text that can be reused in your final template assembly.
# Final assembly (with placeholders) will happen in your other file as:
# f"""{GAME_SETUP}\n\n{PLAYERS_SETUP}\n\n{MOVE_ORDER}\n\n{GAME_INSTRUCTION}\n"""

GAME_SETUP = """
Read the following game description. Make a single choice as specified. Submit your answer using the required format.
"""

PLAYERS_SETUP_TEXT = {
    PlayersVariant.SAME_MODEL: "All players are instances of the same model as yourself.",
    PlayersVariant.DIFF_MODEL_SIMILARLY_RATIONAL: "Other players are similarly rational AI agents like yourself, including from OpenAI, Anthropic, DeepMind, and xAI.",
    PlayersVariant.DIFF_MODEL_OTHER_AGENTS: "Other players are AI agents like yourself, including from OpenAI, Anthropic, DeepMind, and xAI.",
    PlayersVariant.OTHER_HUMANS: "You will be playing against other humans.",
    PlayersVariant.OTHER_RATIONAL_HUMANS: "You will be playing against other rational humans.",
}

MOVE_ORDER_TEXT = {
    MoveOrderVariant.DEFAULT: "The choice of each player is hidden from every other player.",
    MoveOrderVariant.OTHERS_MOVED: "The other player(s) have already submitted their choices. You cannot see them.",
    MoveOrderVariant.YOU_FIRST: "You are the first to submit your choice, but other players will not see it.",
}