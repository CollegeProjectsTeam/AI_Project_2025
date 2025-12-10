class NashPureSolver:
    @staticmethod
    def find_nash_pure(payoffs):
        """
        payoffs[i][j] = [p1, p2]
        return: listă de echilibre Nash (i, j) în indexare 0-based.
        """
        m = len(payoffs)
        n = len(payoffs[0])

        solutions = []

        for i in range(m):       # strategii P1
            for j in range(n):   # strategii P2

                p1_ij, p2_ij = payoffs[i][j]

                # Condiție P1: payoff maxim pe coloană j
                best_for_p1 = True
                for ii in range(m):
                    if payoffs[ii][j][0] > p1_ij:
                        best_for_p1 = False
                        break
                if not best_for_p1:
                    continue

                # Condiție P2: payoff maxim pe rândul i
                best_for_p2 = True
                for jj in range(n):
                    if payoffs[i][jj][1] > p2_ij:
                        best_for_p2 = False
                        break
                if not best_for_p2:
                    continue

                solutions.append((i, j))

        return solutions
