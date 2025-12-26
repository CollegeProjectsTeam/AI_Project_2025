# core/console/nash_utils.py

def read_int_in_range(prompt, min_v, max_v, default=None):
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            val = int(raw)
            if val < min_v or val > max_v:
                print(f"Value must be between {min_v} and {max_v}.")
                continue
            return val
        except ValueError:
            print("Please enter an integer.")


def parse_nash_answer(answer_str, m, n, payoffs=None):
    s = answer_str.strip().lower()
    if s in ("none", "nu", "no", "0", "niciunul", "nici unul"):
        return [], True

    cleaned = answer_str.replace("(", " ").replace(")", " ").replace(";", " ")
    tokens = cleaned.replace(",", " ").split()

    nums = []
    for tok in tokens:
        try:
            nums.append(int(tok))
        except ValueError:
            continue

    pairs = []
    for i in range(0, len(nums), 2):
        if i + 1 >= len(nums):
            break
        r, c = nums[i], nums[i + 1]
        if 1 <= r <= m and 1 <= c <= n:
            pairs.append((r - 1, c - 1))

    pairs = list(set(pairs))

    if not pairs and payoffs is not None and len(nums) == 2:
        pay1, pay2 = nums
        payoff_matches = []
        for i in range(m):
            for j in range(n):
                p1v, p2v = payoffs[i][j]
                if p1v == pay1 and p2v == pay2:
                    payoff_matches.append((i, j))
        if len(payoff_matches) == 1:
            pairs = payoff_matches

    return pairs, False


def evaluate_nash_answer(correct_eqs, user_eqs, user_said_none):
    if not correct_eqs:
        if user_said_none and not user_eqs:
            return 100.0, [], [], []
        else:
            return 0.0, [], [], user_eqs

    correct_set = set(correct_eqs)
    user_set = set(user_eqs)

    hits = list(correct_set & user_set)
    missing = list(correct_set - user_set)
    wrong = list(user_set - correct_set)

    score = 100.0 * len(hits) / len(correct_set)
    return round(score, 2), hits, missing, wrong


def format_eq_list(eq_list):
    if not eq_list:
        return "-"
    return ", ".join(f"({i+1},{j+1})" for i, j in eq_list)
