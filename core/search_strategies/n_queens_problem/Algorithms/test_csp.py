import sys
import os
sys.path.append(os.path.dirname(__file__))

from csp_backtracking import CSP_Backtracking_NQueens

partial = {0: 1}
solver = CSP_Backtracking_NQueens(4, partial)

solution, steps = solver.solve("FC")

print("SOLUTION:", solution)
print("\n--- STEPS ---")
for s in steps:
    print(s)
