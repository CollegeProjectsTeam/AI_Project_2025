from collections import deque

def bidirectional_search(start_state, goal_state, is_complete, generate_options, is_valid):
    front_start = {tuple(start_state)}
    front_goal = {tuple(goal_state)}
    queue_start = deque([start_state])
    queue_goal = deque([goal_state])
    while queue_start and queue_goal:
        current_start = queue_start.popleft()
        if tuple(current_start) in front_goal:
            #print("Solutie gasita:", current_start)
            return current_start
        for option in generate_options(current_start):
            if is_valid(option, current_start):
                new_state = current_start + [option]
                t = tuple(new_state)
                if t not in front_start:
                    front_start.add(t)
                    queue_start.append(new_state)
        current_goal = queue_goal.popleft()
        if tuple(current_goal) in front_start:
            print("Solutie gasita:", current_goal)
            return current_goal
        for option in generate_options(current_goal):
            if is_valid(option, current_goal):
                new_state = current_goal + [option]
                t = tuple(new_state)
                if t not in front_goal:
                    front_goal.add(t)
                    queue_goal.append(new_state)
    return None


# def is_complete_nqueens(solution, n):
#     return len(solution) == n


# def generate_options_nqueens(solution, n):
#     return list(range(n))


# def is_valid_nqueens(col, solution):
#     row = len(solution)
#     for r, c in enumerate(solution):
#         if c == col or abs(c - col) == abs(r - row):
#             return False
#     return True


# def solve_nqueens(board):
#     n = len(board)
#     initial_state = []
#     for row in range(n):
#         for col in range(n):
#             if board[row][col] == 1:
#                 initial_state.append(col)
#     return bidirectional_search(
#         initial_state,
#         [None] * n,
#         lambda sol: is_complete_nqueens(sol, n),
#         lambda sol: generate_options_nqueens(sol, n),
#         is_valid_nqueens
#     )

def solve_nqueens(board):
    return None