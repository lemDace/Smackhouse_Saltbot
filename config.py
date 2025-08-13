# config.py
DEFAULT_CONFIG = {
    "negativity_threshold": -0.3,
    "salt_penalty_curse": 1.0,
    "salt_penalty_insult": 5.0,
    "curse_words": ["damn", "hell", "shit", "fuck", "bitch"],
    "insult_words": ["idiot", "stupid", "moron", "loser", "jerk"],
    "ranks": [
        [500, "Salt King"],
        [300, "Salt Queen"],
        [100, "Salty Sweet"],
        [10,  "Salt Peasant"],
        [0,   "Sugar Babe"],
    ],
    "mention_amplifies": True
}
