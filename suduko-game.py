import tkinter as tk
from tkinter import messagebox
import numpy as np
import random
import threading

# ------------------ Sudoku Logic ------------------ #

def generate_empty_board(size):
    return np.zeros((size, size), dtype="int8")


def find_empty_cell(board):
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                return i, j
    return None


def check_validity(board, row, col, num):
    # Check row
    if num in board[row]:
        return False

    # Check column
    if num in board[:, col]:
        return False

    # Check 3x3 box
    box_size = 3
    start_row = (row // box_size) * box_size
    start_col = (col // box_size) * box_size

    for i in range(start_row, start_row + box_size):
        for j in range(start_col, start_col + box_size):
            if board[i][j] == num:
                return False

    return True


def solve_sudoku(board):
    empty = find_empty_cell(board)

    if not empty:
        return True

    row, col = empty

    numbers = list(range(1, 10))
    random.shuffle(numbers)

    for num in numbers:
        if check_validity(board, row, col, num):
            board[row][col] = num

            if solve_sudoku(board):
                return True

            board[row][col] = 0

    return False


def generate_unsolved_puzzle(board, difficulty):
    if difficulty == "Easy":
        blanks = 30
    elif difficulty == "Medium":
        blanks = 40
    else:
        blanks = 50

    count = 0

    while count < blanks:
        row = random.randint(0, 8)
        col = random.randint(0, 8)

        if board[row][col] != 0:
            board[row][col] = 0
            count += 1


# ------------------ Game Window ------------------ #

def solve_sudoku_threaded(board, callback):

    def solve():
        success = solve_sudoku(board)
        callback(success)

    thread = threading.Thread(target=solve)
    thread.start()


def start_game(difficulty, timer_duration):

    board = generate_empty_board(9)

    def on_solve_complete(success):

        if success:

            solved_board = board.copy()

            generate_unsolved_puzzle(board, difficulty)

            initial_board = board.copy()

            game_window(board, solved_board, initial_board, timer_duration)

        else:
            messagebox.showerror("Error", "Could not generate Sudoku!")

    solve_sudoku_threaded(board, on_solve_complete)


def game_window(board, solved_board, initial_board, timer_duration):

    current_row = 0
    current_col = 0

    hints_used = 0
    max_hints = 3

    incorrect_entries = 0

    grid_labels = []

    time_left = timer_duration

    window = tk.Tk()
    window.title("Sudoku Game")
    window.configure(bg="#f0f0f0")

    size = 9

    # ---------------- Timer ---------------- #

    timer_label = tk.Label(
        window,
        text="",
        font=("Arial", 14, "bold"),
        bg="#f0f0f0"
    )

    timer_label.grid(row=0, column=0, columnspan=size, pady=10)

    def update_timer():
        nonlocal time_left

        if time_left > 0:

            minutes, seconds = divmod(time_left, 60)

            timer_label.config(
                text=f"Time Left: {minutes:02}:{seconds:02}"
            )

            time_left -= 1

            window.after(1000, update_timer)

        else:
            messagebox.showinfo("Time Up", "Game Over!")
            window.destroy()

    update_timer()

    # ---------------- Highlight ---------------- #

    def highlight_cell(row, col):

        for i in range(size):
            for j in range(size):

                bg_color = "#E6F7FF"

                if board[i][j] != 0:
                    bg_color = "#DFFFD6"

                grid_labels[i][j].config(bg=bg_color)

        grid_labels[row][col].config(bg="#FFD580")

    # ---------------- Cell Click ---------------- #

    def on_cell_click(event):
        nonlocal current_row, current_col

        current_row = event.widget.row
        current_col = event.widget.col

        highlight_cell(current_row, current_col)

    # ---------------- Arrow Keys ---------------- #

    def move_focus(event):
        nonlocal current_row, current_col

        if event.keysym == "Up" and current_row > 0:
            current_row -= 1

        elif event.keysym == "Down" and current_row < 8:
            current_row += 1

        elif event.keysym == "Left" and current_col > 0:
            current_col -= 1

        elif event.keysym == "Right" and current_col < 8:
            current_col += 1

        highlight_cell(current_row, current_col)

    # ---------------- Enter Value ---------------- #

    def enter_value(event):

        nonlocal incorrect_entries

        if event.char.isdigit():

            number = int(event.char)

            if 1 <= number <= 9:

                if initial_board[current_row][current_col] != 0:
                    return

                if solved_board[current_row][current_col] == number:

                    board[current_row][current_col] = number

                    grid_labels[current_row][current_col].config(
                        text=str(number),
                        bg="#DFFFD6"
                    )

                    if np.array_equal(board, solved_board):

                        messagebox.showinfo(
                            "Congratulations!",
                            "You solved the Sudoku!"
                        )

                        window.destroy()

                else:

                    incorrect_entries += 1

                    grid_labels[current_row][current_col].config(
                        bg="#FFCCCB"
                    )

                    if incorrect_entries >= 3:
                        messagebox.showinfo(
                            "Game Over",
                            "You made 3 incorrect entries!"
                        )

                        window.destroy()

    # ---------------- Hint ---------------- #

    def provide_hint():

        nonlocal hints_used

        if hints_used >= max_hints:

            messagebox.showinfo(
                "Hint Limit",
                "You already used all hints!"
            )

            return

        empty_cells = []

        for i in range(size):
            for j in range(size):

                if board[i][j] == 0:
                    empty_cells.append((i, j))

        if empty_cells:

            row, col = random.choice(empty_cells)

            board[row][col] = solved_board[row][col]

            grid_labels[row][col].config(
                text=str(solved_board[row][col]),
                bg="#DFFFD6"
            )

            hints_used += 1

    # ---------------- Solve ---------------- #

    def reveal_solution():

        for i in range(size):
            for j in range(size):

                grid_labels[i][j].config(
                    text=str(solved_board[i][j]),
                    bg="#DFFFD6"
                )

    # ---------------- Reset ---------------- #

    def reset_board():

        for i in range(size):
            for j in range(size):

                board[i][j] = initial_board[i][j]

                value = board[i][j]

                grid_labels[i][j].config(
                    text=str(value) if value != 0 else "",
                    bg="#DFFFD6" if value != 0 else "#E6F7FF"
                )

    # ---------------- Sudoku Grid ---------------- #

    for i in range(size):

        row_labels = []

        for j in range(size):

            value = board[i][j]

            bg_color = "#DFFFD6" if value != 0 else "#E6F7FF"

            cell = tk.Label(
                window,
                text=str(value) if value != 0 else "",
                font=("Arial", 18),
                width=4,
                height=2,
                borderwidth=1,
                relief="solid",
                bg=bg_color
            )

            cell.grid(row=i + 1, column=j)

            cell.row = i
            cell.col = j

            cell.bind("<Button-1>", on_cell_click)

            row_labels.append(cell)

        grid_labels.append(row_labels)

    # ---------------- Buttons ---------------- #

    hint_button = tk.Button(
        window,
        text="Hint",
        command=provide_hint,
        width=10,
        bg="#FFD580"
    )

    hint_button.grid(row=11, column=0, columnspan=2, pady=10)

    solve_button = tk.Button(
        window,
        text="Solve",
        command=reveal_solution,
        width=10,
        bg="#28a745",
        fg="white"
    )

    solve_button.grid(row=11, column=2, columnspan=2, pady=10)

    reset_button = tk.Button(
        window,
        text="Reset",
        command=reset_board,
        width=10,
        bg="#ff6347",
        fg="white"
    )

    reset_button.grid(row=11, column=4, columnspan=2, pady=10)

    quit_button = tk.Button(
        window,
        text="Quit",
        command=window.destroy,
        width=10,
        bg="#6C757D",
        fg="white"
    )

    quit_button.grid(row=11, column=6, columnspan=2, pady=10)

    # ---------------- Keyboard Bindings ---------------- #

    window.bind("<Up>", move_focus)
    window.bind("<Down>", move_focus)
    window.bind("<Left>", move_focus)
    window.bind("<Right>", move_focus)

    window.bind("<Key>", enter_value)

    highlight_cell(0, 0)

    window.mainloop()


# ------------------ Main Menu ------------------ #

def main_menu():

    def start():

        difficulty = difficulty_var.get()

        try:
            timer_duration = int(timer_var.get())

        except:
            messagebox.showerror("Error", "Enter valid timer!")
            return

        main.destroy()

        start_game(difficulty, timer_duration)

    main = tk.Tk()

    main.title("Sudoku Menu")

    main.geometry("400x350")

    main.configure(bg="#f0f8ff")

    tk.Label(
        main,
        text="Welcome to Sudoku!",
        font=("Arial", 20, "bold"),
        bg="#f0f8ff",
        fg="#1B4F72"
    ).pack(pady=15)

    tk.Label(
        main,
        text="Select Difficulty:",
        font=("Arial", 14),
        bg="#f0f8ff"
    ).pack(pady=5)

    difficulty_var = tk.StringVar(value="Easy")

    tk.OptionMenu(
        main,
        difficulty_var,
        "Easy",
        "Medium",
        "Hard"
    ).pack(pady=5)

    tk.Label(
        main,
        text="Set Timer (seconds):",
        font=("Arial", 14),
        bg="#f0f8ff"
    ).pack(pady=5)

    timer_var = tk.StringVar(value="300")

    tk.Entry(
        main,
        textvariable=timer_var,
        font=("Arial", 14),
        width=10
    ).pack(pady=5)

    tk.Button(
        main,
        text="Start Game",
        command=start,
        font=("Arial", 14, "bold"),
        bg="#85C1E9",
        fg="white",
        width=15
    ).pack(pady=15)

    tk.Button(
        main,
        text="Quit",
        command=main.destroy,
        font=("Arial", 14, "bold"),
        bg="#6C757D",
        fg="white",
        width=15
    ).pack(pady=5)

    main.mainloop()


# ------------------ Run Program ------------------ #

if __name__ == "__main__":
    main_menu()