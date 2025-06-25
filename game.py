from js import document, setTimeout            # type: ignore
from pyodide.ffi import create_proxy            # type: ignore
import random

# Initial State
board           = [""] * 9        # empty grid
current_player  = "X"             # X always starts
mode            = "pvp"           # default mode

WIN_LINES = [
    (0,1,2),(3,4,5),(6,7,8),      # rows
    (0,3,6),(1,4,7),(2,5,8),      # cols
    (0,4,8),(2,4,6)               # diagonals
]

# DOM elements
cells       = list(document.querySelectorAll(".cell"))
status_el   = document.getElementById("status")
reset_btn   = document.getElementById("reset")
mode_radios = document.getElementsByName("mode")

# Checks winner with respect the current board state and win lines
def winner(brd=None):
    brd = brd or board
    for a,b,c in WIN_LINES:
        if brd[a] and brd[a]==brd[b]==brd[c]:
            return brd[a]
    if "" not in brd:
        return "Draw"
    return None

def render():
    for i,cell in enumerate(cells):
        cell.textContent = board[i]          
    result = winner()
    if result == "Draw":
        status_el.textContent = "It's a draw!"
    elif result:
        status_el.textContent = f"Player {result} wins!"
    else:
        status_el.textContent = f"Player {current_player}'s turn"

# MinMax - Difficulty
def minimax(brd, turn):

    # Evaluation Function
    res = winner(brd)

    if res == "O":
        return 1, None
    elif res == "X":
        return -1, None
    elif res == "Draw":
        return 0, None

    # Set worst case values: -2,2 doesn't exist in this context
    if turn == "O":         # for ai
        best_score = -2
        best_move = None
    else:                   # for user
        best_score = 2
        best_move = None
    
    # Finding the best possible move
    for i in range(9):
        if brd[i]:
            continue
        brd[i] = turn
        next_turn = "X" if turn == "O" else "O"
        score, _ = minimax(brd, next_turn)      # Recursive Function
        brd[i] = ""                             # Backtracking (undoing the simulated move)

        if turn == "O":                         # ai maximizing
            if score > best_score:
                best_score = score
                best_move = i
        else:                                   # user minimizing
            if score < best_score:
                best_score = score
                best_move = i

    return best_score, best_move

def ai_move():
    global current_player
    _, move = minimax(board.copy(), "O")  # score,move - score determines how good the move is - not necessary

    # For random AI comment above & uncomment next two lines:

    # empty = [i for i,v in enumerate(board) if not v] # fetches the empty positions in the board
    # move = random.choice(empty) # uses 'random' to update the ai choice

    board[move] = "O"
    current_player = "X"
    render()

# On click event handling
def on_cell_click(evt):
    global current_player

    idx = int(evt.target.getAttribute("data-idx")) # index of clicked cell

    if board[idx] or winner():
        return                                # ignore illegal move
    
    board[idx] = current_player
    
    if current_player == "X":
        current_player = "O"
    else:
        current_player = "X"

    render()

    if mode == "ai" and current_player == "O" and not winner():
        setTimeout(create_proxy(ai_move), 120) # time delay for the ai_move function

def restart(_=None):
    global board, current_player
    board = [""] * 9
    current_player = "X"
    render()

def on_mode_change(evt):
    global mode
    mode = evt.target.value
    restart()                                 # fresh game on mode switch

# create_proxy: converts python function to js compatible - event handling
for cell in cells:
    cell.addEventListener("click", create_proxy(on_cell_click))
reset_btn.addEventListener("click", create_proxy(restart))
for r in mode_radios:
    r.addEventListener("change", create_proxy(on_mode_change)) # for changing mode

render()  # initial draw - first function
