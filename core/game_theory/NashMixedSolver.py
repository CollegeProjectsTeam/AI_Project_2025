class NashMixedSolver:
    """
    Solver pentru echilibru Nash în strategii mixte pentru jocuri 2x2.
    payoffs[i][j] = [u1, u2]
    i = rând (strategia jucătorului 1), j = coloană (strategia jucătorului 2)
    """

    @staticmethod
    def solve_2x2(payoffs, tol: float = 1e-9):
        """
        Întoarce un dict cu:
          {
            "p": probabilitate P1(A1),
            "q": probabilitate P2(B1),
            "type": "2x2_mixed",
            "support_p1": (0, 1),
            "support_p2": (0, 1)
          }
        sau None dacă nu există un EN mixt interior (0 < p,q < 1).
        """
        m = len(payoffs)
        n = len(payoffs[0]) if m > 0 else 0
        if m != 2 or n != 2:
            return None

        # Payoff-uri pentru jucătorul 1
        a = payoffs[0][0][0]  # A1,B1
        b = payoffs[0][1][0]  # A1,B2
        c = payoffs[1][0][0]  # A2,B1
        d = payoffs[1][1][0]  # A2,B2

        # Payoff-uri pentru jucătorul 2
        e = payoffs[0][0][1]  # A1,B1
        f = payoffs[0][1][1]  # A1,B2
        g = payoffs[1][0][1]  # A2,B1
        h = payoffs[1][1][1]  # A2,B2

        # q = prob P2(B1) astfel încât P1 e indiferent între A1 și A2
        denom_q = a - b - c + d
        # p = prob P1(A1) astfel încât P2 e indiferent între B1 și B2
        denom_p = e - g - f + h

        if abs(denom_q) < tol or abs(denom_p) < tol:
            return None

        q = (d - b) / denom_q
        p = (h - g) / denom_p

        # trebuie să fie în (0,1) ca să fie cu adevărat mixt
        if not (0.0 - tol < p < 1.0 + tol and 0.0 - tol < q < 1.0 + tol):
            return None

        # clamp ușor la [0,1] pentru erori numerice
        p = min(max(p, 0.0), 1.0)
        q = min(max(q, 0.0), 1.0)

        # verificăm indiferența (nu doar formulele)
        EU_A1 = q * a + (1 - q) * b
        EU_A2 = q * c + (1 - q) * d
        if abs(EU_A1 - EU_A2) > 1e-6:
            return None

        EU_B1 = p * e + (1 - p) * g
        EU_B2 = p * f + (1 - p) * h
        if abs(EU_B1 - EU_B2) > 1e-6:
            return None

        return {
            "p": p,              # P1 joacă A1 cu prob p, A2 cu 1-p
            "q": q,              # P2 joacă B1 cu prob q, B2 cu 1-q
            "type": "2x2_mixed",
            "support_p1": (0, 1),
            "support_p2": (0, 1),
        }

    @staticmethod
    def has_mixed(payoffs) -> bool:
        """Convenience: există un EN mixt interior? (doar 2x2)"""
        return NashMixedSolver.solve_2x2(payoffs) is not None