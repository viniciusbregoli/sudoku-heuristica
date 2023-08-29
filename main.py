import pygame
import sys
import random
import heapq

sys.setrecursionlimit(10000)
pygame.init()
pygame.display.set_caption("Sudoku")

# CONSTANTES =======================================================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARKER_GRAY = (210, 210, 210)

BUTTON_WIDTH = 280  # Largura dos botões
BUTTON_HEIGHT = 60  # Altura dos botões
BUTTON_MARGIN = 20  # Espaço entre os botões


CELL_SIZE = 600 // 9

HEIGHT = 9 * CELL_SIZE + BUTTON_MARGIN * 2 + BUTTON_HEIGHT
WIDTH = 9 * CELL_SIZE
# ===================================================================================================

screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont(None, 55)

# Funções ===========================================================================================


def get_block_start(row, col):
    return (row // 3) * 3, (col // 3) * 3


def draw_grid():
    # Draw thinner lines
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, 9 * CELL_SIZE))
    for y in range(0, 9 * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

    # Draw thicker lines
    for x in range(0, WIDTH, 3 * CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, 9 * CELL_SIZE), 3)
    for y in range(0, 9 * CELL_SIZE, 3 * CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y), 3)
    pygame.draw.line(
        screen, BLACK, (0, 9 * CELL_SIZE), (WIDTH, 9 * CELL_SIZE), 3
    )


def draw_numbers():
    for row in range(9):
        for col in range(9):
            if board[row][col] != 0:
                if initial_positions and (row, col) in initial_positions:
                    color = (0, 0, 255)
                else:
                    color = BLACK
                if running:
                    pygame.draw.rect(
                        screen,
                        WHITE,
                        (
                            col * CELL_SIZE,
                            row * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE,
                        ),
                    )  # Clears the cell before drawing the number
                num_text = font.render(str(board[row][col]), True, color)
                screen.blit(
                    num_text, (col * CELL_SIZE + 15, row * CELL_SIZE + 10)
                )


def draw_buttons():
    button1_rect = pygame.Rect(
        (WIDTH - 2 * BUTTON_WIDTH - 1.5 * BUTTON_MARGIN)
        // 2,  # Ajust in x position
        9 * CELL_SIZE + BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    button2_rect = pygame.Rect(
        (WIDTH + 0.5 * BUTTON_MARGIN) // 2,  # Ajust in x position
        9 * CELL_SIZE + BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    pygame.draw.rect(screen, DARKER_GRAY, button1_rect)
    pygame.draw.rect(screen, DARKER_GRAY, button2_rect)

    font = pygame.font.SysFont(None, 30)
    button1_text = font.render("Solve for greedy search", True, BLACK)
    button2_text = font.render("Solve for A*", True, BLACK)

    # Centralizing the text
    button1_text_pos = (
        button1_rect.centerx - button1_text.get_width() // 2,
        button1_rect.centery - button1_text.get_height() // 2,
    )
    button2_text_pos = (
        button2_rect.centerx - button2_text.get_width() // 2,
        button2_rect.centery - button2_text.get_height() // 2,
    )

    screen.blit(button1_text, button1_text_pos)
    screen.blit(button2_text, button2_text_pos)


def draw_highlights():
    if not selected_cell:
        return

    row, col = selected_cell
    block_start_row, block_start_col = get_block_start(row, col)

    pygame.draw.rect(
        screen, DARKER_GRAY, (0, row * CELL_SIZE, 9 * CELL_SIZE, CELL_SIZE)
    )

    # Highlighting the column
    pygame.draw.rect(
        screen, DARKER_GRAY, (col * CELL_SIZE, 0, CELL_SIZE, 9 * CELL_SIZE)
    )

    # Highlighting the block
    for i in range(3):
        for j in range(3):
            pygame.draw.rect(
                screen,
                DARKER_GRAY,
                (
                    (block_start_col + j) * CELL_SIZE,
                    (block_start_row + i) * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                ),
            )


def button_clicked(mouse_pos, button_rect):
    return button_rect.collidepoint(mouse_pos)


def solve(board):
    empty = find_empty_cell(board)
    if not empty:
        return True

    row, col = empty
    numbers = list(range(1, 10))
    random.shuffle(numbers)

    for num in numbers:
        if is_valid(board, num, row, col):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0

    return False


def is_valid(board, num, row, col):
    # Verify row
    for i in range(9):
        if board[row][i] == num:
            return False

    # Verify column
    for i in range(9):
        if board[i][col] == num:
            return False

    # Verify block
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[i + start_row][j + start_col] == num:
                return False

    return True


def find_empty_cell(board, original_board=None):
    if original_board is None:
        original_board = board
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0 and original_board[i][j] == 0:
                return (i, j)
    return None

def generate_sudoku():
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve(board)
    return board

board = generate_sudoku()

def remove_numbers(board, num_to_remove=30):
    # Create a list of all cells
    cells = [(i, j) for i in range(9) for j in range(9)]

    # Shuffle the list
    random.shuffle(cells)

    # Remove the numbers one by one
    for i in range(num_to_remove):
        row, col = cells[i]
        board[row][col] = 0

    return board


def greedy_search(board):
    global original_board
    empty = find_empty_cell(board, original_board)
    if not empty:
        return True

    row, col = empty
    possibilities = get_possibilities(board, row, col)

    if not possibilities:
        return False

    # Orders the possibilities by the number of possibilities for each cell
    possibilities.sort(key=lambda num: len(get_possibilities(board, row, col, num)))

    for num in possibilities:
        if is_valid(board, num, row, col):
            board[row][col] = num
            pygame.time.wait(10)  # Adds a delay for visualization
            draw_numbers()  # Redraws the numbers on the board
            draw_grid()  # Redraws the grid
            check_for_quit()  # Verify if the user clicked on the close button
            pygame.display.flip()  # Updates the display
            if greedy_search(board):
                return True
            board[row][col] = 0
    return False


def get_possibilities(board, row, col, current_number=None):
    # Returns a list of all possible numbers for a given cell
    possibilities = []
    for num in range(1, 10):
        if num == current_number:
            continue
        if is_valid(board, num, row, col):
            possibilities.append(num)
    return possibilities


def check_for_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


# ===================================================================================================
running = False
selected_cell = None
remove_numbers(board, 50)
fixed_numbers = [[False for _ in range(9)] for _ in range(9)]
for i in range(9):
    for j in range(9):
        if board[i][j] != 0:
            fixed_numbers[i][j] = True
for row in board:
    print(row)
initial_positions = set()
for i in range(9):
    for j in range(9):
        if board[i][j] != 0:
            initial_positions.add((i, j))


def a_star(board):
    priority_queue = [(g(board) + h(board), [row[:] for row in board])]
    while priority_queue:
        _, current_board = heapq.heappop(priority_queue)
        for i in range(9):
            for j in range(9):
                board[i][j] = current_board[i][j]
        pygame.time.wait(10)  # Adds a delay for visualization
        draw_numbers()  # Redraws the numbers on the board
        draw_grid()  # Redraws the grid
        check_for_quit()  # Verify if the user clicked on the close button
        pygame.display.flip()  # Updates the display
        if h(current_board) == 0: 
            return
        row, col = find_empty_cell(current_board)
        for num in range(1, 10):
            if is_valid(current_board,num, row, col):
                new_board = [row[:] for row in current_board]
                new_board[row][col] = num
                heapq.heappush(priority_queue, (g(new_board) + h(new_board), new_board))

# Function to calculate g(n) - number of filled cells
def g(board):
    return sum(cell != 0 for row in board for cell in row)

# Function to calculate h(n) - number of empty cells
def h(board):
    return sum(cell == 0 for row in board for cell in row)

def game_loop():
    global selected_cell
    global original_board
    global running
    button1_rect = pygame.Rect(
        (WIDTH - 2 * BUTTON_WIDTH - BUTTON_MARGIN) // 2,
        9 * CELL_SIZE + BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    button2_rect = pygame.Rect(
        (WIDTH + BUTTON_MARGIN) // 2,
        9 * CELL_SIZE + BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if button_clicked((mouse_x, mouse_y), button1_rect):
                    original_board = [row.copy() for row in board]
                    running = True
                    greedy_search(board)
                elif button_clicked((mouse_x, mouse_y), button2_rect):
                    running = True
                    a_star(board)
                else:
                    cell_row, cell_col = (
                        mouse_y // CELL_SIZE,
                        mouse_x // CELL_SIZE,
                    )

                    # Verify if the click was inside the board
                    if 0 <= cell_row < 9 and 0 <= cell_col < 9:
                        # Select the cell if it's empty
                        if board[cell_row][cell_col] == 0:
                            selected_cell = (cell_row, cell_col)
                        else:
                            # Unselect the cell if it's already selected
                            selected_cell = None

            if event.type == pygame.KEYDOWN:
                if event.unicode.isdigit() and selected_cell:
                    row, col = selected_cell
                    # Verify if the number is fixed
                    if not fixed_numbers[row][col]:
                        num = int(event.unicode)
                        if is_valid(board, num, row, col):
                            board[row][col] = num
                            selected_cell = None
        screen.fill(WHITE)
        draw_highlights()
        draw_numbers()
        draw_grid()
        draw_buttons()
        pygame.display.flip()

game_loop()