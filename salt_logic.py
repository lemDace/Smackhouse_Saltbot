# salt_logic.py
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database import cur, conn

analyzer = SentimentIntensityAnalyzer()

curse_rx = None
insult_rx = None

def build_word_boundary_regex(words: set):
    if not words:
        return None
    pattern = r"\b(?:" + "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True)) + r")\b"
    return re.compile(pattern, re.IGNORECASE)

def rebuild_regexes(config):
    global curse_rx, insult_rx
    curse_rx = build_word_boundary_regex(config["curse_words"])
    insult_rx = build_word_boundary_regex(config["insult_words"])

def today_utc_str():
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%d")

def current_week_bounds_utc():
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")

def get_user_salt(user_id: int):
    cur.execute("SELECT salt FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return float(row["salt"]) if row else 0.0

def set_user_salt(user_id: int, value: float):
    cur.execute("INSERT OR REPLACE INTO users (user_id, salt) VALUES (?, ?)", (user_id, value))
    conn.commit()

def add_user_salt(user_id: int, amount: float):
    date_str = today_utc_str()
    cur.execute("INSERT OR IGNORE INTO users (user_id, salt) VALUES (?, 0)", (user_id,))
    cur.execute("UPDATE users SET salt = salt + ? WHERE user_id = ?", (amount, user_id))
    cur.execute("INSERT OR IGNORE INTO history (user_id, date, amount) VALUES (?, ?, 0)", (user_id, date_str))
    cur.execute("UPDATE history SET amount = amount + ? WHERE user_id = ? AND date = ?", (amount, user_id, date_str))
    conn.commit()

def get_rank_for_total(total: float, config):
    ranks_sorted = sorted(config["ranks"], key=lambda x: x[0], reverse=True)
    for th, name in ranks_sorted:
        if total >= float(th):
            return name
    return "Unranked"

def calculate_salt(text: str, mentions: int, config) -> float:
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]
    found_curse = bool(curse_rx.search(text)) if curse_rx else False
    found_insult = bool(insult_rx.search(text)) if insult_rx else False
    directed = config.get("mention_amplifies", True) and (mentions > 0)
    salt_inc = 0.0
    if found_curse or found_insult:
        if found_insult or (found_curse and (compound < config["negativity_threshold"] or directed)):
            salt_inc = float(config["salt_penalty_insult"])
        else:
            salt_inc = float(config["salt_penalty_curse"])
    return salt_inc
