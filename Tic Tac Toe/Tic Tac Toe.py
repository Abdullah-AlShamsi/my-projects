import pygame as pg
import sys
import time
from random import choice, randint

pg.init()

# Constants
WIDTH, HEIGHT = 500, 500
CELL_SIZE = 120
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
blank_img = pg.image.load('Blank.png')
x_img = pg.image.load('x.png')
o_img = pg.image.load('o.png')
background_img = pg.image.load('Background.jpg')
tie_img = pg.image.load('Tie Game.png')

# Scale images
background_img = pg.transform.scale(background_img, (WIDTH, HEIGHT))
tie_img = pg.transform.scale(tie_img, (WIDTH, HEIGHT))
x_img = pg.transform.scale(x_img, (CELL_SIZE, CELL_SIZE))
o_img = pg.transform.scale(o_img, (CELL_SIZE, CELL_SIZE))
blank_img = pg.transform.scale(blank_img, (CELL_SIZE, CELL_SIZE))

# Window setup
win = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Tic Tac Toe')
clock = pg.time.Clock()

# Game variables
winners = [[1,2,3],[4,5,6],[7,8,9],[1,4,7],[2,5,8],[3,6,9],[1,5,9],[3,5,7]]
bord = ['' for _ in range(10)]
turn = 'x'
won = False
move = True
compMove = 5
startX = startY = endX = endY = 0
button_font = pg.font.SysFont(None, 30)
restart_rect = pg.Rect(WIDTH // 2 - 130, HEIGHT - 60, 100, 40)
back_rect = pg.Rect(WIDTH // 2 + 30, HEIGHT - 60, 100, 40)
game_mode = None

class Square(pg.sprite.Sprite):
    def __init__(self, x_id, y_id, number):
        super().__init__()
        self.width = CELL_SIZE
        self.height = CELL_SIZE
        self.x = x_id * self.width
        self.y = y_id * self.height
        self.content = ''
        self.number = number
        self.image = blank_img
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.rect.center = (self.x, self.y)

    def Clicked(self, x_val, y_val):
        global turn
        if self.content == '' and self.rect.collidepoint(x_val, y_val):
            self.content = turn
            bord[self.number] = turn
            if turn == 'x':
                self.image = x_img
                turn = 'o'
                checkWinner('x')
                if not won and game_mode != 'Human Vs Human':
                    CompMove()
            else:
                self.image = o_img
                turn = 'x'
                checkWinner('o')
            if not won and game_mode == 'Human Vs Human':
                checkDraw()

square_group = pg.sprite.Group()
squares = []

def reset_game():
    global bord, turn, won, move, compMove, squares, square_group, background_img
    bord = ['' for _ in range(10)]
    turn = 'x'
    won = False
    move = True
    compMove = 5
    background_img = pg.image.load('Background.jpg')
    background_img = pg.transform.scale(background_img, (WIDTH, HEIGHT))
    squares.clear()
    square_group.empty()
    num = 1
    for y in range(1, 4):
        for x in range(1, 4):
            sq = Square(x, y, num)
            square_group.add(sq)
            squares.append(sq)
            num += 1

def getPos(n1, n2):
    global startX, startY, endX, endY
    for sqs in squares:
        if sqs.number == n1:
            startX, startY = sqs.x, sqs.y
        elif sqs.number == n2:
            endX, endY = sqs.x, sqs.y

def drawLine(x1, y1, x2, y2):
    pg.draw.line(win, BLACK, (x1, y1), (x2, y2), 10)
    pg.display.update()
    time.sleep(1)

def checkWinner(player):
    global won, background_img
    for i in range(8):
        if bord[winners[i][0]] == bord[winners[i][1]] == bord[winners[i][2]] == player:
            won = True
            getPos(winners[i][0], winners[i][2])
            break
    if won:
        Update()
        drawLine(startX, startY, endX, endY)
        square_group.empty()
        background_img = pg.image.load(player.upper() + ' Wins.png')
        background_img = pg.transform.scale(background_img, (WIDTH, HEIGHT))

def checkDraw():
    global background_img
    if all(cell != '' for cell in bord[1:]) and not won:
        square_group.empty()
        try:
            background_img = tie_img
        except:
            font = pg.font.SysFont(None, 80)
            background_img.fill(WHITE)
            text = font.render("It's a tie!", True, BLACK)
            background_img.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

def Update():
    win.blit(background_img, (0, 0))
    square_group.draw(win)
    square_group.update()
    pg.draw.rect(win, WHITE, restart_rect)
    pg.draw.rect(win, WHITE, back_rect)

    restart_text = button_font.render("Restart", True, BLACK)
    back_text = button_font.render("Back", True, BLACK)

    win.blit(restart_text, restart_text.get_rect(center=restart_rect.center))
    win.blit(back_text, back_text.get_rect(center=back_rect.center))
    pg.display.update()

def CompMove():
    global move
    move = True

    if game_mode == 'Weak AI':
        checkRandom()

    elif game_mode == 'Intermediate AI':
        if randint(0, 2):  # ~66% chance to make smart move
            Winner('o')
            if move: Winner('x')
            if move: checkCenter()
            if move: checkCorner()
            if move: checkEdge()
        else:
            checkRandom()

    elif game_mode == 'Strong AI':
        print("Strong AI: Using Alpha-Beta Pruning (always)")
        best = minimax(bord[:], True, -float('inf'), float('inf'))
        if best['index']:
            for square in squares:
                if square.number == best['index']:
                    square.Clicked(square.x, square.y)
                    return

    elif game_mode == 'Adaptive AI':
        empty_cells = bord[1:].count('')
        if empty_cells >= 6:
            print("Adaptive AI: Using standard Minimax (early game)")
            best = pure_minimax(bord[:], True)
        else:
            print("Adaptive AI: Switching to Alpha-Beta Pruning (mid/late game)")
            best = minimax(bord[:], True, -float('inf'), float('inf'))
        if best['index']:
            for square in squares:
                if square.number == best['index']:
                    square.Clicked(square.x, square.y)
                    return

    if not move:
        for square in squares:
            if square.number == compMove:
                square.Clicked(square.x, square.y)
                return

    Update()
    time.sleep(1)
    checkDraw()

def checkRandom():
    global compMove, move
    empty = [i for i in range(1, 10) if bord[i] == '']
    if empty:
        compMove = choice(empty)
        move = False

def Winner(player):
    global compMove, move
    for i in range(8):
        line = winners[i]
        if bord[line[0]] == bord[line[1]] == player and bord[line[2]] == '':
            compMove = line[2]
            move = False
            return
        elif bord[line[0]] == bord[line[2]] == player and bord[line[1]] == '':
            compMove = line[1]
            move = False
            return
        elif bord[line[1]] == bord[line[2]] == player and bord[line[0]] == '':
            compMove = line[0]
            move = False
            return

def checkCenter():
    global compMove, move
    if bord[5] == '':
        compMove = 5
        move = False

def checkCorner():
    global compMove, move
    for i in [1, 3, 7, 9]:
        if bord[i] == '':
            compMove = i
            move = False
            break

def checkEdge():
    global compMove, move
    for i in [2, 4, 6, 8]:
        if bord[i] == '':
            compMove = i
            move = False
            break

def makeMove(pos, player):
    bord[pos] = player
    for s in squares:
        if s.number == pos:
            s.content = player
            s.image = o_img if player == 'o' else x_img
            break

def pure_minimax(board, isMax):
    winner = get_winner(board)
    if winner == 'o':
        return {'score': 1, 'index': None}
    elif winner == 'x':
        return {'score': -1, 'index': None}
    elif '' not in board[1:]:
        return {'score': 0, 'index': None}

    best = {'score': -float('inf'), 'index': None} if isMax else {'score': float('inf'), 'index': None}

    for i in range(1, 10):
        if board[i] == '':
            board[i] = 'o' if isMax else 'x'
            sim_result = pure_minimax(board[:], not isMax)
            board[i] = ''
            sim_result['index'] = i

            if isMax:
                if sim_result['score'] > best['score']:
                    best = sim_result
            else:
                if sim_result['score'] < best['score']:
                    best = sim_result

    return best

def minimax(board, isMax, alpha, beta):
    winner = get_winner(board)
    if winner == 'o':
        return {'score': 1, 'index': None}
    elif winner == 'x':
        return {'score': -1, 'index': None}
    elif '' not in board[1:]:
        return {'score': 0, 'index': None}

    best = {'score': -float('inf'), 'index': None} if isMax else {'score': float('inf'), 'index': None}

    for i in range(1, 10):
        if board[i] == '':
            board[i] = 'o' if isMax else 'x'
            sim_result = minimax(board[:], not isMax, alpha, beta)
            board[i] = ''
            sim_result['index'] = i

            if isMax:
                if sim_result['score'] > best['score']:
                    best = sim_result
                alpha = max(alpha, best['score'])
            else:
                if sim_result['score'] < best['score']:
                    best = sim_result
                beta = min(beta, best['score'])

            if beta <= alpha:
                break

    return best

def get_winner(board):
    for line in winners:
        a, b, c = line
        if board[a] == board[b] == board[c] and board[a] != '':
            return board[a]
    return None

def show_menu():
    font = pg.font.SysFont(None, 40)
    win.blit(background_img, (0, 0))
    options = ['Human Vs Human', 'Weak AI', 'Intermediate AI', 'Strong AI', 'Adaptive AI']
    buttons = []
    for i, text in enumerate(options):
        label = font.render(text, True, BLACK)
        rect = label.get_rect(center=(WIDTH//2, 100 + i * 80))
        pg.draw.rect(win, WHITE, rect.inflate(20, 10))  # Optional button background
        win.blit(label, rect)
        buttons.append((text, rect))
    pg.display.update()
    return buttons

# Main loop
showing_menu = True
while True:
    clock.tick(FPS)
    if showing_menu:
        buttons = show_menu()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                mx, my = pg.mouse.get_pos()
                for text, rect in buttons:
                    if rect.collidepoint((mx, my)):
                        game_mode = text
                        showing_menu = False
                        reset_game()
    else:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                mx, my = pg.mouse.get_pos()
                if restart_rect.collidepoint((mx, my)):
                    reset_game()
                elif back_rect.collidepoint((mx, my)):
                    showing_menu = True
                    background_img = pg.image.load('Background.jpg')
                    background_img = pg.transform.scale(background_img, (WIDTH, HEIGHT))
                elif not won and game_mode == 'Human Vs Human':
                    for s in squares:
                        s.Clicked(mx, my)
                elif not won and turn == 'x':
                    for s in squares:
                        s.Clicked(mx, my)
        Update()
