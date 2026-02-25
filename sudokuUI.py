import ctypes
import tkinter as tk
from tkinter import messagebox
import time


# get C functions from the library
lib = ctypes.CDLL("./lib/sudoku.so")
lib.solveSudoku.argtypes = [ctypes.POINTER(ctypes.c_int)]
lib.solveSudoku.restype  = ctypes.c_int


#  COLORS
COAL_BROWN = "#423e37"
PAC_CYAN = "#508991"
EGGSHELL = "#edebd7"
ROSY_GRANITE = "#a39594"
DIM_GREY = "#6e675f"

BG          = EGGSHELL      # window background
BOX_LINE    = COAL_BROWN    # 3×3 borders
CELL_LINE   = DIM_GREY      # inner cell borders
CELL_BG     = EGGSHELL      # cell background
CELL_HOV    = "#BBBAA9"     # hovered cell
GIVEN_FG    = COAL_BROWN    # digits the user typed
SOLVED_FG   = "#B1304A"     # digits filled by the solver

BTN_BG      = "#e94560"     # Solve and clear button
BTN_FG      = EGGSHELL 
BTN_HOV     = "#B1304A"
CLEAR_BG    = PAC_CYAN 
CLEAR_FG    = EGGSHELL
CLEAR_HOV   = "#4B7587"

TITLE_FG    = PAC_CYAN 

FONT_CELL   = ("Arial", 20, "bold")
FONT_TITLE  = ("Arial", 26, "bold")
FONT_BTN    = ("Arial", 12, "bold")
FONT_TIMER  = ("Arial", 8, "bold")

THIN        = 1
THICK       = 3



class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku Solver")
        self.geometry("720x720")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.cells = [[{} for i in range(9)] for j in range(9)]
        self._given = [[False] * 9 for i in range(9)]   # True if user gave an input 
        self._build_ui()


    def _build_ui(self):
        # Title
        tk.Label(self, text="SUDOKU SOLVER", font=FONT_TITLE,
                 fg=TITLE_FG, bg=BG).pack(pady=(24, 16))

        # Grid canvas area
        outer = tk.Frame(self, bg=BOX_LINE, padx=THICK, pady=THICK)
        outer.pack(padx=24)
        self._build_grid(outer)

        # Buttons
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=20)

        self._timer_label = tk.Label(self, text="", font=FONT_TIMER, fg=COAL_BROWN, bg=BG)
        self._timer_label.place(x=12, rely=1.0, anchor="sw", y=-10)

        self._make_button(btn_row, "SOLVE",      self._solve,  BTN_BG,   BTN_FG,   BTN_HOV  ).pack(side="left", padx=8)
        self._make_button(btn_row, "CLEAR",      self._clear,  CLEAR_BG, CLEAR_FG, CLEAR_HOV).pack(side="left", padx=8)

    def _make_button(self, parent, text, command, bg, fg, hover_bg):
        btn = tk.Label(parent, text=text, font=FONT_BTN,
                       bg=bg, fg=fg, cursor="hand2",
                       padx=22, pady=10, relief="flat")
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def _build_grid(self, parent):
        for box_row in range(3):
            for box_col in range(3):
                # Frame for each 3×3 box
                box = tk.Frame(parent, bg=BOX_LINE,
                               padx=THIN, pady=THIN)
                # gap between boxes 
                pad_top  = THICK if box_row > 0 else 0
                pad_left = THICK if box_col > 0 else 0
                box.grid(row=box_row, column=box_col,
                         padx=(pad_left, 0), pady=(pad_top, 0))

                for row in range(3):
                    for col in range(3):
                        i = box_row * 3 + row
                        j = box_col * 3 + col
                        self._make_cell(box, i, j, row, col)

    def _make_cell(self, parent, i, j, r, c):
        var = tk.StringVar()
        frame = tk.Frame(parent, bg=CELL_LINE,
                         padx=THIN, pady=THIN)
        pad_top  = THIN if r > 0 else 0
        pad_left = THIN if c > 0 else 0
        frame.grid(row=r, column=c,
                   padx=(pad_left, 0), pady=(pad_top, 0))

        entry = tk.Entry(
            frame,
            textvariable=var,
            width=3,
            font=FONT_CELL,
            fg=GIVEN_FG,
            bg=CELL_BG,
            insertbackground=GIVEN_FG,
            relief="flat",
            justify="center",
            validate="key",
            validatecommand=(self.register(self._validate), "%P"),
        )
        entry.pack(ipady=10, ipadx=4)

        # Hover effect
        entry.bind("<Enter>", lambda e, w=entry: w.config(bg=CELL_HOV))
        entry.bind("<Leave>", lambda e, w=entry: w.config(bg=CELL_BG))

        # Arrow keys 
        entry.bind("<Up>",    lambda e, ii=i, jj=j: self._focus(ii-1, jj))
        entry.bind("<Down>",  lambda e, ii=i, jj=j: self._focus(ii+1, jj))
        entry.bind("<Left>",  lambda e, ii=i, jj=j: self._focus(ii,   jj-1))
        entry.bind("<Right>", lambda e, ii=i, jj=j: self._focus(ii,   jj+1))

        self.cells[i][j] = {"entry": entry, "var": var}


    def _validate(self, val):
        #Allow only empty or a single digit 1-9
        return val == "" or (len(val) == 1 and val in "123456789")

    def _focus(self, i, j):
        if 0 <= i < 9 and 0 <= j < 9:
            self.cells[i][j]["entry"].focus_set()

    def _set_cell(self, i, j, value: int, fg: str, editable: bool):
        cell = self.cells[i][j]
        cell["var"].set(str(value) if value else "")
        cell["entry"].config(
            fg=fg,
            bg=CELL_BG,
            state="normal" if editable else "disabled",
            disabledforeground=fg,
            disabledbackground=CELL_BG,
        )

    def _read_board(self):
        # Reads the board and return a board[81] list
        board = []
        for i in range(9):
            for j in range(9):
                val = self.cells[i][j]["var"].get()
                board.append(int(val) if val else 0)
        return board

    def _solve(self):
        board = self._read_board()

        # Remember which cells the user filled in
        for i in range(9):
            for j in range(9):
                self._given[i][j] = board[i * 9 + j] != 0

        arr = (ctypes.c_int * 81)(*board)

        startt = time.perf_counter()
        if not lib.solveSudoku(arr):
            messagebox.showerror("No Solution",
                                 "This puzzle has no solution.")
            return
        elapsed_time = (time.perf_counter()-startt) * 1000

        self._timer_label.config(text=f"time: {elapsed_time:.2f} ms")

        solution = list(arr)
        for i in range(9):
            for j in range(9):
                val = solution[i * 9 + j]
                if self._given[i][j]:
                    self._set_cell(i, j, val, GIVEN_FG, editable=False)
                else:
                    self._set_cell(i, j, val, SOLVED_FG, editable=False)

    def _clear(self):
        self._timer_label.config(text="")
        for i in range(9):
            for j in range(9):
                self._set_cell(i, j, 0, GIVEN_FG, editable=True)
                self._given[i][j] = False



if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()






