from itertools import combinations

class SudokuCell:
    def __init__(self, value=0):
        self.value = value
        self.candidates = set(range(1, 10)) if value == 0 else set()

def get_all_units(board):
    units = []

    for row in board.grid:
        units.append(row)

    for col in range(9):
        units.append([board.grid[row][col] for row in range(9)])

    for box_row in range(3):
        for box_col in range(3):
            box = []
            for i in range(3):
                for j in range(3):
                    r = 3 * box_row + i
                    c = 3 * box_col + j
                    box.append(board.grid[r][c])
            units.append(box)

    return units

class SudokuBoard:
    def __init__(self, grid):
        self.grid = [[SudokuCell(value) for value in row] for row in grid]
        self.update_all_candidates()
        self.difficulty = 0

    def update_all_candidates(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i][j].value == 0:
                    self.grid[i][j].candidates = self.get_candidates(i, j)
                else:
                    self.grid[i][j].candidates = set()

    def get_candidates(self, row, col):
        if self.grid[row][col].value != 0:
            return set()
        used = set()
        used.update(self.get_row_values(row))
        used.update(self.get_col_values(col))
        used.update(self.get_box_values(row, col))
        return set(range(1, 10)) - used

    def get_row_values(self, row):
        return {self.grid[row][j].value for j in range(9) if self.grid[row][j].value != 0}

    def get_col_values(self, col):
        return {self.grid[i][col].value for i in range(9) if self.grid[i][col].value != 0}

    def get_box_values(self, row, col):
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        return {
            self.grid[r][c].value
            for r in range(start_row, start_row + 3)
            for c in range(start_col, start_col + 3)
            if self.grid[r][c].value != 0
        }

    def is_solved(self):
        return all(self.grid[i][j].value != 0 for i in range(9) for j in range(9))

    def get_possible_candidates(board, row, col):
        existing = set()
        existing |= {board.grid[row][c].value for c in range(9) if board.grid[row][c].value != 0}
        existing |= {board.grid[r][col].value for r in range(9) if board.grid[r][col].value != 0}

        box_r, box_c = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if board.grid[r][c].value != 0:
                    existing.add(board.grid[r][c].value)

        return set(range(1, 10)) - existing

    def apply_naked_singles(board):
        progress = False
        for i in range(9):
            for j in range(9):
                cell = board.grid[i][j]
                if cell.value == 0 and len(cell.candidates) == 1:
                    cell.value = cell.candidates.pop()
                    print("naked single found")
                    board.update_all_candidates() 

                    board.difficulty+=8
                    progress = True
        return progress

    def apply_hidden_singles(board):
        progress = False
        for unit in get_all_units(board): 
            counter = {digit: [] for digit in range(1, 10)}
            for cell in unit:
                if cell.value == 0:
                    for candidate in cell.candidates:
                        counter[candidate].append(cell)
            
            for digit, cells in counter.items():
                if len(cells) == 1:
                    target_cell = cells[0]
                    target_cell.value = digit
                    target_cell.candidates.clear()
                    board.update_all_candidates()
                    print("hidden single found")
                    
                    board.difficulty+=3
                    progress = True
        return progress

    def apply_pointing_pairs_triples(board):
        progress = False

        for box_row in range(3):
            for box_col in range(3):
                box_cells = [
                    (r, c)
                    for r in range(box_row * 3, box_row * 3 + 3)
                    for c in range(box_col * 3, box_col * 3 + 3)
                    if board.grid[r][c].value == 0
                ]

                for digit in range(1, 10):
                    positions = [(r, c) for (r, c) in box_cells if digit in board.grid[r][c].candidates]

                    if 2 <= len(positions) <= 3:
                        rows = set(r for r, c in positions)
                        cols = set(c for r, c in positions)

                        if len(rows) == 1:
                            row = next(iter(rows))
                            for c in range(9):
                                if c // 3 != box_col and digit in board.grid[row][c].candidates:
                                    board.grid[row][c].candidates.discard(digit)
                                    print("pointing pair/triple found")
                                    
                                    board.difficulty +=9
                                    progress = True

                        if len(cols) == 1:
                            col = next(iter(cols))
                            for r in range(9):
                                if r // 3 != box_row and digit in board.grid[r][col].candidates:
                                    board.grid[r][col].candidates.discard(digit)
                                    print("pointing pair/triple found")
                                    board.difficulty +=9
                                    progress = True

        return progress
    
    def apply_box_line_reduction(board):
        progress = False

        for row in range(9):
            for digit in range(1, 10):
                cols_with_digit = [col for col in range(9) if digit in board.grid[row][col].candidates]

                if 2 <= len(cols_with_digit) <= 3:
                    boxes = set(col // 3 for col in cols_with_digit)
                    if len(boxes) == 1:
                        box_col = boxes.pop()
                        box_row = row // 3
                        for r in range(box_row * 3, box_row * 3 + 3):
                            if r == row:
                                continue
                            for c in range(box_col * 3, box_col * 3 + 3):
                                if digit in board.grid[r][c].candidates:
                                    board.grid[r][c].candidates.discard(digit)
                                    print("box-line reduction found")
                                    
                                    board.difficulty +=20
                                    progress = True

        for col in range(9):
            for digit in range(1, 10):
                rows_with_digit = [row for row in range(9) if digit in board.grid[row][col].candidates]

                if 2 <= len(rows_with_digit) <= 3:
                    boxes = set(row // 3 for row in rows_with_digit)
                    if len(boxes) == 1:
                        box_row = boxes.pop()
                        box_col = col // 3
                        for c in range(box_col * 3, box_col * 3 + 3):
                            if c == col:
                                continue
                            for r in range(box_row * 3, box_row * 3 + 3):
                                if digit in board.grid[r][c].candidates:
                                    board.grid[r][c].candidates.discard(digit)
                                    print("box-line reduction found")
                                    board.difficulty +=20
                                    progress = True

        return progress
    
    def apply_naked_pairs(board):
        progress = False

        for unit in get_all_units(board): 
            candidate_map = {}

            for cell in unit:
                if cell.value == 0 and len(cell.candidates) == 2:
                    key = frozenset(cell.candidates)
                    candidate_map.setdefault(key, []).append(cell)

            for candidate_pair, cells_with_pair in candidate_map.items():
                if len(cells_with_pair) == 2:
                    for cell in unit:
                        if cell not in cells_with_pair and cell.value == 0:
                            before = len(cell.candidates)
                            cell.candidates -= candidate_pair
                            if len(cell.candidates) < before:
                                print("naked pair found")
                                
                                board.difficulty+=27.5#35 for triple
                                progress = True

        return progress

    def apply_hidden_pairs(board):
        progress = False

        for unit in get_all_units(board): 
            digit_positions = {d: [] for d in range(1, 10)}

            for cell in unit:
                if cell.value == 0:
                    for d in cell.candidates:
                        digit_positions[d].append(cell)

            for d1, d2 in combinations(range(1, 10), 2):
                cells_d1 = digit_positions[d1]
                cells_d2 = digit_positions[d2]

                if len(cells_d1) == 2 and cells_d1 == cells_d2:
                    for cell in cells_d1:
                        before = set(cell.candidates)
                        if cell.candidates != {d1, d2}:
                            cell.candidates &= {d1, d2}
                            if cell.candidates != before:
                                print("Hidden pair found")
                                board.difficulty+=37.5 #55 for triple
                                progress = True

        return progress

    def apply_x_wing(board):

        progress = False

        for digit in range(1, 10):
            row_positions = []
            for row in range(9):
                cols = [col for col in range(9) if digit in board.grid[row][col].candidates]
                if len(cols) == 2:
                    row_positions.append((row, tuple(cols)))

            for i in range(len(row_positions)):
                for j in range(i + 1, len(row_positions)):
                    r1, cols1 = row_positions[i]
                    r2, cols2 = row_positions[j]
                    if cols1 == cols2:
                        c1, c2 = cols1
                        for row in range(9):
                            if row != r1 and row != r2:
                                for col in [c1, c2]:
                                    cell = board.grid[row][col]
                                    if digit in cell.candidates:
                                        cell.candidates.discard(digit)
                                        print("X-Wing found")
                                        board.difficulty += 45
                                        progress = True

            col_positions = []
            for col in range(9):
                rows = [row for row in range(9) if digit in board.grid[row][col].candidates]
                if len(rows) == 2:
                    col_positions.append((col, tuple(rows)))

            for i in range(len(col_positions)):
                for j in range(i + 1, len(col_positions)):
                    c1, rows1 = col_positions[i]
                    c2, rows2 = col_positions[j]
                    if rows1 == rows2:
                        r1, r2 = rows1
                        for col in range(9):
                            if col != c1 and col != c2:
                                for row in [r1, r2]:
                                    cell = board.grid[row][col]
                                    if digit in cell.candidates:
                                        cell.candidates.discard(digit)
                                        print("X-Wing found")
                                        board.difficulty += 45
                                        progress = True

        return progress

    def apply_chute_remote_pairs(board):
        progress = False

        for digit in range(1, 10):
            positions = [(r, c) for r in range(9) for c in range(9) if digit in board.grid[r][c].candidates]

            for (r1, c1), (r2, c2) in combinations(positions, 2):
                if r1 // 3 == r2 // 3 and c1 // 3 == c2 // 3:
                    continue

                if r1 == r2 or c1 == c2:
                    continue

                if (r1 // 3 == r2 // 3) or (c1 // 3 == c2 // 3):
                    continue

                for r in range(9):
                    for c in range(9):
                        if (r != r1 and r != r2) and (c != c1 and c != c2):
                            cell = board.grid[r][c]
                            if digit in cell.candidates:
                                cell.candidates.discard(digit)
                                print("chute remote pair found")
                                board.difficulty+=150
                                progress = True

        return progress
    
    def apply_hidden_triples(board):
        board.difficulty+=18
        progress = False

        for unit in get_all_units(board):
            digit_positions = {d: [] for d in range(1, 10)}

            for cell in unit:
                if cell.value == 0:
                    for d in cell.candidates:
                        digit_positions[d].append(cell)

            for d1, d2, d3 in combinations(range(1, 10), 3):
                cells_d1 = set(digit_positions[d1])
                cells_d2 = set(digit_positions[d2])
                cells_d3 = set(digit_positions[d3])

                combined_cells = cells_d1 | cells_d2 | cells_d3

                if len(combined_cells) == 3:
                    for cell in combined_cells:
                        before = set(cell.candidates)
                        cell.candidates &= {d1, d2, d3} 
                        if cell.candidates != before:
                            print("hidden triple found")
                            board.difficulty += 55
                            progress = True

        return progress

    def apply_naked_triples(board):
        board.difficulty+=18

        progress = False

        for unit in get_all_units(board): 
            candidate_map = {}

            for cell in unit:
                if cell.value == 0 and 2 <= len(cell.candidates) <= 3:
                    key = frozenset(cell.candidates)
                    candidate_map.setdefault(key, []).append(cell)

            for triple_candidates in combinations(candidate_map.keys(), 3):
                combined_candidates = set().union(*triple_candidates)
                if len(combined_candidates) == 3:
                    triple_cells = set()
                    for candidates in triple_candidates:
                        triple_cells.update(candidate_map[candidates])

                    if len(triple_cells) == 3:
                        for cell in unit:
                            if cell not in triple_cells and cell.value == 0:
                                before = len(cell.candidates)
                                cell.candidates -= combined_candidates
                                if len(cell.candidates) < before:
                                    print("naked triple found")
                                    board.difficulty += 35
                                    progress = True

        return progress

    def solve(self):
        techniques = [
            self.apply_hidden_singles,
            self.apply_naked_singles,
            self.apply_pointing_pairs_triples,
            self.apply_box_line_reduction,
            self.apply_hidden_pairs,
            self.apply_naked_pairs,
            self.apply_x_wing,
            self.apply_naked_triples,
            self.apply_hidden_triples,
            self.apply_chute_remote_pairs
        ]

        while True:
            progress = False
            for technique in techniques:
                if technique():
                    progress = True
                    break
            if not progress:
                break

        if not self.is_solved():
            print("not possible to solve with given techniques/invalid sudoku puzzle:")
            return self

        return self

# example_board = [ #easy
#     [5, 3, 0, 2, 9, 0, 0, 0, 4],
#     [0, 0, 2, 7, 4, 3, 5, 0, 0],
#     [4, 0, 9, 0, 5, 0, 1, 3, 0],
#     [0, 0, 0, 5, 8, 0, 0, 0, 7],
#     [0, 8, 0, 0, 2, 4, 9, 0, 0],
#     [2, 0, 0, 1, 0, 9, 0, 0, 0],
#     [0, 0, 5, 0, 0, 2, 8, 7, 1],
#     [0, 9, 0, 0, 0, 7, 0, 0, 0],
#     [7, 2, 6, 8, 0, 0, 3, 0, 9]
# ]

# example_board = [ # medium
#     [0, 9, 0, 5, 1, 0, 0, 7, 2],
#     [5, 0, 7, 0, 0, 4, 0, 0, 1],
#     [0, 6, 3, 8, 7, 2, 5, 4, 9],
#     [7, 0, 8, 9, 0, 6, 0, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 6, 0],
#     [6, 0, 0, 3, 4, 7, 0, 0, 8],
#     [0, 0, 0, 4, 0, 0, 1, 0, 7],
#     [0, 0, 5, 2, 8, 1, 3, 9, 0],
#     [0, 0, 0, 0, 3, 0, 0, 0, 0]
# ]

example_board = [ #medium
    [0, 0, 0, 6, 0, 0, 0, 0, 7],
    [0, 7, 8, 0, 0, 0, 0, 0, 5],
    [2, 0, 5, 0, 0, 0, 6, 0, 0],
    [0, 0, 2, 0, 0, 1, 3, 4, 0],
    [0, 0, 0, 2, 0, 0, 0, 0, 1],
    [8, 0, 0, 7, 4, 0, 0, 5, 6],
    [0, 9, 0, 8, 6, 0, 1, 3, 0],
    [1, 0, 6, 0, 7, 0, 5, 0, 8],
    [0, 0, 0, 0, 0, 9, 0, 0, 0]
]


# example_board = [ extreme
#     [0, 0, 2, 0, 3, 0, 0, 0, 0],
#     [0, 6, 0, 0, 0, 0, 0, 3, 1],
#     [4, 1, 0, 8, 0, 0, 0, 7, 0],
#     [5, 0, 0, 3, 0, 0, 0, 0, 0],
#     [0, 9, 0, 0, 0, 0, 0, 0, 6],
#     [0, 4, 0, 2, 0, 8, 0, 9, 0],
#     [0, 0, 0, 6, 8, 2, 0, 0, 4],
#     [7, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 5, 9, 0, 0, 6,0]
# ]

# example_board = [  #extreme
#     [9, 0, 0, 3, 1, 0, 0, 0, 0],
#     [0, 8, 0, 0, 0, 0, 3, 0, 0],
#     [2, 0, 0, 0, 0, 0, 0, 0, 7],
#     [0, 6, 4, 8, 0, 0, 0, 0, 0],
#     [0, 0, 7, 0, 0, 4, 2, 0, 0],
#     [0, 0, 0, 0, 0, 6, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 7, 4, 6],
#     [0, 0, 0, 0, 5, 0, 0, 8, 0],
#     [0, 0, 0, 0, 8, 9, 0, 2, 0]
# ]

# example_board = [ #easy
#   [0, 0, 1, 9, 0, 0, 8, 0, 0],
#   [0, 2, 9, 6, 5, 3, 7, 4, 1],
#   [5, 0, 0, 0, 0, 0, 0, 3, 0],
#   [6, 0, 4, 1, 7, 8, 5, 0, 0],
#   [0, 8, 7, 0, 3, 0, 0, 9, 4],
#   [3, 5, 2, 0, 4, 6, 1, 8, 7],
#   [7, 0, 8, 0, 0, 1, 3, 0, 9],
#   [2, 1, 0, 0, 6, 0, 0, 0, 0],
#   [0, 0, 3, 5, 0, 7, 0, 0, 6]
# ]

# example_board = [ #medium
#   [7, 0, 0, 0, 9, 0, 2, 0, 1],
#   [0, 0, 0, 7, 0, 0, 0, 0, 3],
#   [0, 0, 0, 3, 0, 1, 0, 8, 0],
#   [1, 0, 0, 4, 5, 0, 0, 0, 0],
#   [0, 0, 0, 0, 0, 0, 6, 0, 0],
#   [9, 5, 0, 0, 0, 0, 0, 0, 0],
#   [0, 0, 3, 0, 7, 8, 0, 0, 4],
#   [0, 0, 0, 6, 0, 0, 0, 1, 0],
#   [0, 0, 0, 9, 0, 4, 8, 7, 0]
# ]

# example_board = [ extreme
#   [2, 0, 6, 0, 0, 0, 0, 0, 0],
#   [0, 0, 0, 8, 0, 0, 0, 0, 3],
#   [0, 9, 0, 0, 0, 2, 0, 0, 1],
#   [0, 3, 0, 0, 0, 4, 0, 5, 0],
#   [0, 5, 8, 2, 0, 0, 0, 0, 0],
#   [0, 0, 0, 5, 1, 0, 0, 8, 0],
#   [0, 0, 0, 0, 0, 0, 0, 0, 9],
#   [0, 0, 5, 0, 9, 7, 1, 3, 0],
#   [0, 0, 9, 3, 0, 8, 2, 0, 0]
# ]

# example_board = [
#   [0, 0, 0, 3, 9, 0, 0, 7, 0],
#   [2, 0, 0, 0, 6, 0, 4, 0, 0],
#   [8, 0, 0, 0, 0, 1, 0, 0, 0],
#   [0, 0, 0, 8, 0, 0, 3, 1, 0],
#   [0, 0, 4, 7, 0, 0, 6, 0, 0],
#   [9, 0, 0, 0, 0, 2, 5, 0, 0],
#   [0, 0, 0, 0, 0, 0, 0, 0, 0],
#   [0, 0, 5, 0, 0, 0, 8, 0, 0],
#   [0, 0, 0, 0, 2, 0, 1, 0, 9]
# ]

example_board = [
  [0, 0, 4, 0, 0, 0, 0, 5, 0],
  [0, 6, 7, 0, 0, 5, 0, 1, 4],
  [0, 1, 0, 4, 0, 0, 0, 0, 8],
  [0, 7, 0, 0, 0, 3, 0, 0, 0],
  [0, 0, 8, 0, 4, 0, 0, 0, 3],
  [0, 0, 0, 9, 0, 1, 5, 0, 0],
  [0, 0, 1, 0, 7, 0, 0, 2, 0],
  [0, 0, 9, 0, 0, 6, 0, 0, 0],
  [6, 0, 5, 0, 3, 0, 0, 7, 0]
]

# example_board = [ #ludicrous - unsolvable
#   [0, 3, 0, 0, 0, 6, 0, 0, 5],
#   [9, 0, 0, 5, 0, 0, 2, 0, 0],
#   [0, 0, 2, 0, 1, 0, 0, 7, 0],
#   [0, 9, 0, 0, 0, 8, 0, 0, 4],
#   [0, 0, 8, 0, 0, 0, 7, 0, 0],
#   [2, 0, 0, 6, 0, 0, 0, 9, 0],
#   [0, 1, 0, 0, 5, 0, 3, 0, 0],
#   [0, 0, 4, 0, 0, 9, 0, 0, 1],
#   [6, 0, 0, 1, 0, 0, 0, 4, 0]
# ]

board = SudokuBoard(example_board)
solved_board = board.solve()

for row in solved_board.grid:
    print([cell.value for cell in row])

print(f"Difficulty: {board.difficulty}")