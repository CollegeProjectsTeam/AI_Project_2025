class CSP_Backtracking_NQueens:
    def __init__(self, board_size, partial_assignment=None):
        self.n = board_size

        # assignment: dict {row: col}
        self.assignment = partial_assignment.copy() if partial_assignment else {}

        # domain: dict {row: [possible_cols]}
        self.domains = {
            r: ([partial_assignment[r]] if partial_assignment and r in partial_assignment
                else list(range(self.n)))
            for r in range(self.n)
        }

        self.steps = []  # explanation log

    # -------------------------------
    # Helper: check if assigning col to row is consistent
    # -------------------------------
    def is_consistent(self, row, col):
        for r, c in self.assignment.items():
            if c == col:  # same column
                return False
            if abs(r - row) == abs(c - col):  # diagonal attack
                return False
        return True

    # -------------------------------
    # MRV variable selection
    # -------------------------------
    def select_unassigned_variable_mrv(self):
        unassigned = [v for v in range(self.n) if v not in self.assignment]
        # choose variable with smallest domain
        return min(unassigned, key=lambda v: len(self.domains[v]))

    # -------------------------------
    # AC-3 queue generation
    # -------------------------------
    def ac3(self):
        from collections import deque
        queue = deque()

        for xi in range(self.n):
            for xj in range(self.n):
                if xi != xj:
                    queue.append((xi, xj))

        while queue:
            xi, xj = queue.popleft()
            if self.revise(xi, xj):
                if len(self.domains[xi]) == 0:
                    return False  # domain wipeout
                for xk in range(self.n):
                    if xk != xi:
                        queue.append((xk, xi))
        return True

    # -------------------------------
    # AC-3 revise
    # -------------------------------
    def revise(self, xi, xj):
        revised = False
        to_remove = []

        for vi in self.domains[xi]:
            # vi is supported if there exists vj in domain[xj] that does not conflict
            supported = False
            for vj in self.domains[xj]:
                if vi != vj and abs(xi - xj) != abs(vi - vj):
                    supported = True
                    break

            if not supported:
                to_remove.append(vi)

        if to_remove:
            for v in to_remove:
                self.domains[xi].remove(v)
            revised = True

        return revised

    # -------------------------------
    # Forward checking
    # -------------------------------
    def forward_checking(self, row, col):
        # remove invalid values in unassigned rows
        for r in range(self.n):
            if r in self.assignment:
                continue
            to_remove = []
            for c in self.domains[r]:
                if c == col or abs(r - row) == abs(c - col):
                    to_remove.append(c)

            if to_remove:
                for c in to_remove:
                    self.domains[r].remove(c)

                if len(self.domains[r]) == 0:
                    return False  # domain wipeout

        return True

    # -------------------------------
    # Backtracking search
    # -------------------------------
    def backtrack(self, strategy):
        # complete if assigned all rows
        if len(self.assignment) == self.n:
            return True

        var = self.select_unassigned_variable_mrv()
        self.steps.append(f"Select variable (row) {var} by MRV, domain={self.domains[var]}")

        for val in list(self.domains[var]):  # copy since domain may shrink
            self.steps.append(f"Try {var} -> {val}")

            if not self.is_consistent(var, val):
                self.steps.append(f"  Inconsistent, skip {var}->{val}")
                continue

            # save copies for undo
            old_assignment = self.assignment.copy()
            old_domains = {k: v.copy() for k, v in self.domains.items()}

            # assign
            self.assignment[var] = val
            self.steps.append(f"  Assign {var}->{val}")

            # constraint propagation
            propagation_ok = True

            if strategy == "FC":
                propagation_ok = self.forward_checking(var, val)
                self.steps.append(f"  Forward checking result: {propagation_ok}")

            elif strategy == "AC3":
                propagation_ok = self.ac3()
                self.steps.append(f"  AC-3 result: {propagation_ok}")

            # If domain wipeout, undo and continue
            if not propagation_ok:
                self.assignment = old_assignment
                self.domains = old_domains
                self.steps.append(f"  Domain wipeout → backtrack")
                continue

            # recursive backtracking
            if self.backtrack(strategy):
                return True

            # undo
            self.assignment = old_assignment
            self.domains = old_domains
            self.steps.append(f"  Undo {var}->{val} (backtrack)")

        return False

    # -------------------------------
    # Public solve() method
    # -------------------------------
    def solve(self, strategy="FC"):
        self.steps.append(f"Start CSP Backtracking N={self.n}, strategy={strategy}")
        ok = self.backtrack(strategy)
        return (self.assignment if ok else None, self.steps)