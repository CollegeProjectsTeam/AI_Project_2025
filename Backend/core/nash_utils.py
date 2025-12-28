def parse_nash_answer(answer_str, m, n, payoffs=None):
    s = (answer_str or "").strip().lower()
    if s in ("none", "no", "nu", "0"):
        return [], True

    cleaned = (answer_str or "").replace("(", " ").replace(")", " ").replace(";", " ")
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
        return "none"
    return ", ".join(f"({i+1},{j+1})" for i, j in eq_list)
