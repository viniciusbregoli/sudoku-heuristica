import pygame
import sys
import random
import heapq

sys.setrecursionlimit(10000)
pygame.init()
pygame.display.set_caption("Sudoku")

# CONSTANTES =======================================================================================
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (200, 200, 200)
DARKER_GRAY = (210, 210, 210)

BUTTON_WIDTH = 280  # Largura dos botões
BUTTON_HEIGHT = 60  # Altura dos botões
BUTTON_MARGIN = 20  # Espaço entre os botões


TAMANHO_BLOCO = 600 // 9

ALTURA = 9 * TAMANHO_BLOCO + BUTTON_MARGIN * 2 + BUTTON_HEIGHT
LARGURA = 9 * TAMANHO_BLOCO
# ===================================================================================================

screen = pygame.display.set_mode((LARGURA, ALTURA))
font = pygame.font.SysFont(None, 55)

# Funções ===========================================================================================


def get_block_start(row, col):
    return (row // 3) * 3, (col // 3) * 3


def draw_grid():
    for x in range(0, LARGURA, TAMANHO_BLOCO):
        pygame.draw.line(screen, CINZA, (x, 0), (x, 9 * TAMANHO_BLOCO))
    for y in range(0, 9 * TAMANHO_BLOCO, TAMANHO_BLOCO):
        pygame.draw.line(screen, CINZA, (0, y), (LARGURA, y))

    # Desenhar as linhas mais grossas para os quadrados 3x3
    for x in range(0, LARGURA, 3 * TAMANHO_BLOCO):
        pygame.draw.line(screen, PRETO, (x, 0), (x, 9 * TAMANHO_BLOCO), 3)
    for y in range(0, 9 * TAMANHO_BLOCO, 3 * TAMANHO_BLOCO):
        pygame.draw.line(screen, PRETO, (0, y), (LARGURA, y), 3)
    pygame.draw.line(
        screen, PRETO, (0, 9 * TAMANHO_BLOCO), (LARGURA, 9 * TAMANHO_BLOCO), 3
    )


def draw_numbers():
    for row in range(9):
        for col in range(9):
            if tabuleiro[row][col] != 0:
                if initial_positions and (row, col) in initial_positions:
                    color = (0, 0, 255)
                else:
                    color = PRETO
                pygame.draw.rect(
                    screen,
                    BRANCO,
                    (
                        col * TAMANHO_BLOCO,
                        row * TAMANHO_BLOCO,
                        TAMANHO_BLOCO,
                        TAMANHO_BLOCO,
                    ),
                )  # Limpa a área antes de desenhar
                num_text = font.render(str(tabuleiro[row][col]), True, color)
                screen.blit(
                    num_text, (col * TAMANHO_BLOCO + 15, row * TAMANHO_BLOCO + 10)
                )


def draw_buttons():
    button1_rect = pygame.Rect(
        (LARGURA - 2 * BUTTON_WIDTH - 1.5 * BUTTON_MARGIN)
        // 2,  # Ajuste no posicionamento x
        9 * TAMANHO_BLOCO + BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    button2_rect = pygame.Rect(
        (LARGURA + 0.5 * BUTTON_MARGIN) // 2,  # Ajuste no posicionamento x
        9 * TAMANHO_BLOCO + BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    pygame.draw.rect(screen, DARKER_GRAY, button1_rect)
    pygame.draw.rect(screen, DARKER_GRAY, button2_rect)

    font = pygame.font.SysFont(None, 30)
    button1_text = font.render("Resolver por Busca Gulosa", True, PRETO)
    button2_text = font.render("Resolver por A*", True, PRETO)

    # Centralizando o texto dentro do botão
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
        screen, DARKER_GRAY, (0, row * TAMANHO_BLOCO, 9 * TAMANHO_BLOCO, TAMANHO_BLOCO)
    )

    # Destacando a coluna
    pygame.draw.rect(
        screen, DARKER_GRAY, (col * TAMANHO_BLOCO, 0, TAMANHO_BLOCO, 9 * TAMANHO_BLOCO)
    )

    # Destacando o bloco 3x3
    for i in range(3):
        for j in range(3):
            pygame.draw.rect(
                screen,
                DARKER_GRAY,
                (
                    (block_start_col + j) * TAMANHO_BLOCO,
                    (block_start_row + i) * TAMANHO_BLOCO,
                    TAMANHO_BLOCO,
                    TAMANHO_BLOCO,
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
    # Verifica linha
    for i in range(9):
        if board[row][i] == num:
            return False

    # Verifica coluna
    for i in range(9):
        if board[i][col] == num:
            return False

    # Verifica quadrado 3x3
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
                return (i, j)  # linha, coluna
    return None


def generate_sudoku():
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve(board)
    return board


tabuleiro = generate_sudoku()


def remove_numbers(board, num_to_remove=30):
    # Criar uma lista de todas as células
    cells = [(i, j) for i in range(9) for j in range(9)]

    # Embaralhar a lista
    random.shuffle(cells)

    # Remover os primeiros 'num_to_remove' números
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

    # Ordena os números por menor quantidade de possibilidades
    possibilities.sort(key=lambda num: len(get_possibilities(board, row, col, num)))

    for num in possibilities:
        if is_valid(board, num, row, col):
            board[row][col] = num
            pygame.time.wait(25)  # Adiciona um atraso para visualização
            draw_numbers()  # Redesenha os números no tabuleiro
            draw_grid()  # Redesenha a grade
            check_for_quit()  # Verifica se o usuário clicou no botão de fechar
            pygame.display.flip()  # Atualiza o display

            if greedy_search(board):
                return True

            board[row][col] = 0
    return False


def get_possibilities(board, row, col, current_number=None):
    # Retorna uma lista dos números possíveis para uma célula específica
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

selected_cell = None
remove_numbers(tabuleiro, 50)
fixed_numbers = [[False for _ in range(9)] for _ in range(9)]
for i in range(9):
    for j in range(9):
        if tabuleiro[i][j] != 0:
            fixed_numbers[i][j] = True
for row in tabuleiro:
    print(row)
initial_positions = set()
for i in range(9):
    for j in range(9):
        if tabuleiro[i][j] != 0:
            initial_positions.add((i, j))


def a_star(board):
    priority_queue = [(g(board) + h(board), [row[:] for row in board])]
    while priority_queue:
        _, current_board = heapq.heappop(priority_queue)
        for i in range(9):
            for j in range(9):
                board[i][j] = current_board[i][j]
        pygame.time.wait(2)  # Adiciona um atraso para visualização
        draw_numbers()  # Redesenha os números no tabuleiro
        draw_grid()  # Redesenha a grade
        check_for_quit()  # Verifica se o usuário clicou no botão de fechar
        pygame.display.flip()  # Atualiza o display
        if h(current_board) == 0: 
            return
        row, col = find_empty_cell(current_board)
        for num in range(1, 10):
            if is_valid_move(current_board, row, col, num):
                new_board = [row[:] for row in current_board]
                new_board[row][col] = num
                heapq.heappush(priority_queue, (g(new_board) + h(new_board), new_board))


def is_valid_move(board, row, col, num):
    for x in range(9):
        if board[row][x] == num:
            return False
    for x in range(9):
        if board[x][col] == num:
            return False
    startRow, startCol = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[i + startRow][j + startCol] == num:
                return False
    return True

# Função para calcular g(n) - número de células preenchidas
def g(board):
    return sum(cell != 0 for row in board for cell in row)

# Função para calcular h(n) - número de células vazias
def h(board):
    return sum(cell == 0 for row in board for cell in row)

def game_loop():
    global selected_cell
    global original_board
    button1_rect = pygame.Rect(
        (LARGURA - 2 * BUTTON_WIDTH - BUTTON_MARGIN) // 2,
        9 * TAMANHO_BLOCO + BUTTON_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    button2_rect = pygame.Rect(
        (LARGURA + BUTTON_MARGIN) // 2,
        9 * TAMANHO_BLOCO + BUTTON_MARGIN,
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
                    print("Botão de Busca Gulosa pressionado!")
                    original_board = [row.copy() for row in tabuleiro]
                    greedy_search(tabuleiro)
                elif button_clicked((mouse_x, mouse_y), button2_rect):
                    print("Botão de A* pressionado!")
                    a_star(tabuleiro)
                else:
                    cell_row, cell_col = (
                        mouse_y // TAMANHO_BLOCO,
                        mouse_x // TAMANHO_BLOCO,
                    )

                    # Verifique se as coordenadas estão dentro da grade
                    if 0 <= cell_row < 9 and 0 <= cell_col < 9:
                        # Selecione a célula se ela estiver vazia
                        if tabuleiro[cell_row][cell_col] == 0:
                            selected_cell = (cell_row, cell_col)
                        else:
                            # Desmarque a seleção atual se uma célula não vazia for clicada
                            selected_cell = None

            if event.type == pygame.KEYDOWN:
                if event.unicode.isdigit() and selected_cell:
                    row, col = selected_cell
                    # Verifique se o número é fixo
                    if not fixed_numbers[row][col]:
                        num = int(event.unicode)
                        if is_valid(tabuleiro, num, row, col):
                            tabuleiro[row][col] = num
                            selected_cell = None

        screen.fill(BRANCO)
        draw_numbers()
        draw_grid()
        draw_highlights()
        draw_buttons()

        pygame.display.flip()


game_loop()
