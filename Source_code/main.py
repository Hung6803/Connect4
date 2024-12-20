import pygame, sys
import numpy as np
from button import Button
import math
import random

pygame.init()

WIDTH, HEIGHT = 750, 750
SCREEN_SIZE = (WIDTH, HEIGHT)

ICON = pygame.image.load("image/icon.png")

SCREEN = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Connect4")
pygame.display.set_icon(ICON)

CHECKBOX = pygame.transform.scale(pygame.image.load("image/unchecked.png"), (20, 20))
CHECKBOX_CHECKKED = pygame.transform.scale(pygame.image.load("image/checked.png"), (20, 20))

BOARD_SIZE = 1
FIRST_PLAYER = 1
TIME_PER_TURN = 1

WINDOW_LENGTH = 4

ROW_COUNT = 6
COLUMN_COUNT = 6

PLAYER = 0
AI = 1

TIME = 15
TURN = random.randint(PLAYER, AI)
COLOR_PLAYER = (255,0,0)
COLOR_AI = (0,0,255)
COLOR_LABEL = (215, 252, 212)
COLOR_BACKGROUND = (52, 78, 91)

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

SQUARESIZE = int(500/(ROW_COUNT + 1))
RADIUS = int(SQUARESIZE/2 - 5)

def get_font(size):
    return pygame.font.Font("font/font.ttf", size)

def create_board():
        board = np.zeros((ROW_COUNT,COLUMN_COUNT))
        return board   

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	# Check ngang
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check dọc
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check chéo lên
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check chéo xuống
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

#Check hòa
def draw_mode(board):
    result = True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 0:
                result =  False
                break
    return result


def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	#Điểm chiếm cột giữa
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	# Điểm chiều ngang
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	# Điểm chiều dọc
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	# Điểm đường chéo
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(board):
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, AI_PIECE):
				return (None, 100000000000000)
			elif winning_move(board, PLAYER_PIECE):
				return (None, -10000000000000)
			else:
				return (None, 0)
		else:
			return (None, score_position(board, AI_PIECE))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else:
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def draw_board(board, x, y, height_board):
    global SQUARESIZE
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(SCREEN, COLOR_LABEL, (x + c*SQUARESIZE, y + r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(SCREEN, "Black", (x + int(c*SQUARESIZE+SQUARESIZE/2), y + int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(SCREEN, COLOR_PLAYER, (x + int(c*SQUARESIZE+SQUARESIZE/2), y + height_board - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(SCREEN, COLOR_AI, (x + int(c*SQUARESIZE+SQUARESIZE/2), y + height_board - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()
        
def play():
    global ROW_COUNT
    global COLUMN_COUNT
    global TURN
    global TIME
    global SQUARESIZE, RADIUS
    GAME_OVER = False

    if BOARD_SIZE == 1:
        ROW_COUNT = 6
        COLUMN_COUNT = 6
    if BOARD_SIZE == 2:
        ROW_COUNT = 7
        COLUMN_COUNT = 7
    if BOARD_SIZE == 3:
        ROW_COUNT = 8
        COLUMN_COUNT = 8
    if FIRST_PLAYER == 1:
        TURN = random.randint(PLAYER, AI)
    if FIRST_PLAYER == 2:
        TURN = PLAYER
    if FIRST_PLAYER == 3:
        TURN = AI
    if TIME_PER_TURN == 1:
        TIME = 15
    if TIME_PER_TURN == 2:
        TIME = 30
    if TIME_PER_TURN == 3:
        TIME = 45
        
    SQUARESIZE = int(500/(ROW_COUNT + 1))
    width_board = COLUMN_COUNT * SQUARESIZE
    height_board = (ROW_COUNT+1) * SQUARESIZE
    RADIUS = int(SQUARESIZE / 2) - 5
    x = int((WIDTH - width_board) / 2)
    y = 230
    turn = TURN
    
    countdown_time = TIME * 1000
    start_time = pygame.time.get_ticks()
    
    board = create_board()
    SCREEN.fill(COLOR_BACKGROUND) 
    draw_board(board, x, y, height_board)

    while not GAME_OVER: 
        pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (20, 40, 400, 150), border_radius= 40)
        pygame.draw.rect(SCREEN, COLOR_LABEL, (20, 40, 400, 150), 10, border_radius= 40)
        pygame.draw.rect(SCREEN, COLOR_LABEL, (440, 40, 150, 150), 10, border_radius= 40)
        pygame.draw.rect(SCREEN, COLOR_LABEL, (x, y, width_board, SQUARESIZE), 5)
        
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_BACK = Button(image=None, pos=(660, 50), 
                            text_input="BACK", font=get_font(25), base_color=COLOR_LABEL, hovering_color="White")
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)
        
        label = get_font(25).render("YOUR TURN", 1, COLOR_PLAYER)
        SCREEN.blit(label, (100,100))
        
        if turn == PLAYER:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time
            pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (440, 40, 150, 150), border_radius= 40)
            pygame.draw.rect(SCREEN, COLOR_LABEL, (440, 40, 150, 150), 10, border_radius= 40)
            remaining_time = int((countdown_time - elapsed_time) / 1000)
            label = get_font(25).render(str(remaining_time), 1, (255, 215, 0))
            SCREEN.blit(label, (500,100))
            
            if elapsed_time >= countdown_time:
                pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (20, 40, 400, 150), border_radius= 40)
                pygame.draw.rect(SCREEN, COLOR_LABEL, (20, 40, 400, 150), 10, border_radius= 40)
                label = get_font(25).render("AI WINS!!", 1, COLOR_AI)
                SCREEN.blit(label, (100,100))
                GAME_OVER = True
            pygame.display.flip()
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (x, y, width_board, SQUARESIZE))
                pygame.draw.rect(SCREEN, COLOR_LABEL, (x, y, width_board, SQUARESIZE), 5)
                posx = event.pos[0]
                if turn == PLAYER:
                    if posx >= int(x + SQUARESIZE/2) and posx <= int(x + width_board - SQUARESIZE/2):
                        pygame.draw.circle(SCREEN, COLOR_PLAYER, (posx, y + int(SQUARESIZE/2)), RADIUS)
                    else:
                        if posx < int(x + SQUARESIZE/2):
                            pygame.draw.circle(SCREEN, COLOR_PLAYER, (x + SQUARESIZE/2, y + int(SQUARESIZE/2)), RADIUS)
                        if posx > int(x + width_board - SQUARESIZE/2):
                            pygame.draw.circle(SCREEN, COLOR_PLAYER, (x + width_board - SQUARESIZE/2, y + int(SQUARESIZE/2)), RADIUS)

            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(SCREEN, COLOR_LABEL, (x, y, width_board, SQUARESIZE), 5)

                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    menu()
                if turn == PLAYER:
                    posx = event.pos[0]
                    if posx >= int(x) and posx <= int(x + width_board):
                        col = int(math.floor((posx - x)/SQUARESIZE))

                        if is_valid_location(board, col):
                            row = get_next_open_row(board, col)
                            drop_piece(board, row, col, PLAYER_PIECE)

                            if winning_move(board, PLAYER_PIECE):
                                pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (20, 40, 400, 150), border_radius= 40)
                                pygame.draw.rect(SCREEN, COLOR_LABEL, (20, 40, 400, 150), 10, border_radius= 40)
                                label = get_font(25).render("YOU WIN!!", 1, COLOR_PLAYER)
                                SCREEN.blit(label, (50,100))
                                
                                GAME_OVER = True

                            if draw_mode(board):
                                pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (20, 40, 400, 150), border_radius= 40)
                                pygame.draw.rect(SCREEN, COLOR_LABEL, (20, 40, 400, 150), 10, border_radius= 40)
                                label = get_font(25).render("HÒA!!", 1, (255, 215, 0))
                                SCREEN.blit(label, (150,100))
                                GAME_OVER = True
                                
                            turn = AI
                            pygame.display.flip()
                            draw_board(board, x, y, height_board)
              
        if turn == AI and not GAME_OVER:
            pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (20, 40, 400, 150), border_radius= 40)
            pygame.draw.rect(SCREEN, COLOR_LABEL, (20, 40, 400, 150), 10, border_radius= 40)
            label = get_font(25).render("AI TURN", 1, COLOR_AI)
            SCREEN.blit(label, (100,100))			
            pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (440, 40, 150, 150), border_radius= 40)
            pygame.draw.rect(SCREEN, COLOR_LABEL, (440, 40, 150, 150), 10, border_radius= 40)
            pygame.display.flip()

            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True) # type: ignore

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (20, 40, 400, 150), border_radius= 40)
                    pygame.draw.rect(SCREEN, COLOR_LABEL, (20, 40, 400, 150), 10, border_radius= 40)
                    label = get_font(25).render("AI WINS!!", 1, COLOR_AI)
                    SCREEN.blit(label, (100,100))
                    GAME_OVER = True
                    
                if draw_mode(board):
                    pygame.draw.rect(SCREEN, COLOR_BACKGROUND, (20, 40, 400, 150), border_radius= 40)
                    pygame.draw.rect(SCREEN, COLOR_LABEL, (20, 40, 400, 150), 10, border_radius= 40)
                    label = get_font(25).render("HÒA!!", 1, (255, 215, 0))
                    SCREEN.blit(label, (150,100))
                    GAME_OVER = True
                draw_board(board, x, y, height_board)

                turn = PLAYER
                start_time = pygame.time.get_ticks()
                pygame.display.flip()

        if GAME_OVER:
            pygame.time.wait(5000)
            menu()

   


def setting():
    
    global FIRST_PLAYER
    global BOARD_SIZE
    global TIME_PER_TURN
    
    def draw_checkbox():
        if BOARD_SIZE == 1:
            SCREEN.blit(CHECKBOX_CHECKKED, (100, 275))
            SCREEN.blit(CHECKBOX, (275, 275))
            SCREEN.blit(CHECKBOX, (450, 275))
        if BOARD_SIZE == 2:
            SCREEN.blit(CHECKBOX, (100, 275))
            SCREEN.blit(CHECKBOX_CHECKKED, (275, 275))
            SCREEN.blit(CHECKBOX, (450, 275))
        if BOARD_SIZE == 3:
            SCREEN.blit(CHECKBOX, (100, 275))
            SCREEN.blit(CHECKBOX, (275, 275))
            SCREEN.blit(CHECKBOX_CHECKKED, (450, 275))
        if FIRST_PLAYER == 1:
            SCREEN.blit(CHECKBOX_CHECKKED, (100, 425))
            SCREEN.blit(CHECKBOX, (275, 425))
            SCREEN.blit(CHECKBOX, (450, 425))
        if FIRST_PLAYER == 2:
            SCREEN.blit(CHECKBOX, (100, 425))
            SCREEN.blit(CHECKBOX_CHECKKED, (275, 425))
            SCREEN.blit(CHECKBOX, (450, 425))
        if FIRST_PLAYER == 3:
            SCREEN.blit(CHECKBOX, (100, 425))
            SCREEN.blit(CHECKBOX, (275, 425))
            SCREEN.blit(CHECKBOX_CHECKKED, (450, 425))
        if TIME_PER_TURN == 1:
            SCREEN.blit(CHECKBOX_CHECKKED, (100, 575))
            SCREEN.blit(CHECKBOX, (275, 575))
            SCREEN.blit(CHECKBOX, (450, 575))
        if TIME_PER_TURN == 2:
            SCREEN.blit(CHECKBOX, (100, 575))
            SCREEN.blit(CHECKBOX_CHECKKED, (275, 575))
            SCREEN.blit(CHECKBOX, (450, 575))
        if TIME_PER_TURN == 3:
            SCREEN.blit(CHECKBOX, (100, 575))
            SCREEN.blit(CHECKBOX, (275, 575))
            SCREEN.blit(CHECKBOX_CHECKKED, (450, 575))
            
    while True:
        
        SCREEN.fill(COLOR_BACKGROUND)
        
        SETTING_MOUSE_POS = pygame.mouse.get_pos()

        SETTING_TEXT = get_font(75).render("SETTING", True, "#b68f40")
        SETTING_RECT = SETTING_TEXT.get_rect(center=(375, 100))
        SCREEN.blit(SETTING_TEXT, SETTING_RECT)

        BOARD_SIZE_TEXT = get_font(25).render("BOARD SIZE", True, COLOR_LABEL)
        BOARD_SIZE_RECT = BOARD_SIZE_TEXT.get_rect(topleft = (50, 200))
        SCREEN.blit(BOARD_SIZE_TEXT, BOARD_SIZE_RECT)
        
        BOARD_SIZE_1_TEXT = get_font(20).render("6x6", True, "Black")
        BOARD_SIZE_1_RECT = BOARD_SIZE_1_TEXT.get_rect(topleft = (125, 275))
        SCREEN.blit(BOARD_SIZE_1_TEXT, BOARD_SIZE_1_RECT)
        
        BOARD_SIZE_2_TEXT = get_font(20).render("7x7", True, "Black")
        BOARD_SIZE_2_RECT = BOARD_SIZE_2_TEXT.get_rect(topleft = (300, 275))
        SCREEN.blit(BOARD_SIZE_2_TEXT, BOARD_SIZE_2_RECT)
        
        BOARD_SIZE_3_TEXT = get_font(20).render("8x8", True, "Black")
        BOARD_SIZE_3_RECT = BOARD_SIZE_3_TEXT.get_rect(topleft = (475, 275))
        SCREEN.blit(BOARD_SIZE_3_TEXT, BOARD_SIZE_3_RECT)
        
        FIRST_PLAYER_TEXT = get_font(25).render("PLAY FIRST", True, COLOR_LABEL)
        FIRST_PLAYER_RECT = FIRST_PLAYER_TEXT.get_rect(topleft = (50, 350))
        SCREEN.blit(FIRST_PLAYER_TEXT, FIRST_PLAYER_RECT)
        
        FIRST_PLAYER_1_TEXT = get_font(20).render("RANDOM", True, "Black")
        FIRST_PLAYER_1_RECT = FIRST_PLAYER_1_TEXT.get_rect(topleft = (125, 425))
        SCREEN.blit(FIRST_PLAYER_1_TEXT, FIRST_PLAYER_1_RECT)
        
        FIRST_PLAYER_2_TEXT = get_font(20).render("PLAYER", True, "Black")
        FIRST_PLAYER_2_RECT = FIRST_PLAYER_2_TEXT.get_rect(topleft = (300, 425))
        SCREEN.blit(FIRST_PLAYER_2_TEXT, FIRST_PLAYER_2_RECT)
        
        FIRST_PLAYER_3_TEXT = get_font(20).render("OPPONENT", True, "Black")
        FIRST_PLAYER_3_RECT = FIRST_PLAYER_3_TEXT.get_rect(topleft = (475, 425))
        SCREEN.blit(FIRST_PLAYER_3_TEXT, FIRST_PLAYER_3_RECT)

        TIME_PER_TURN_TEXT = get_font(25).render("TIME PER TURN", True, COLOR_LABEL)
        TIME_PER_TURN_RECT = TIME_PER_TURN_TEXT.get_rect(topleft = (50, 500))
        SCREEN.blit(TIME_PER_TURN_TEXT, TIME_PER_TURN_RECT)
        
        TIME_PER_TURN_1_TEXT = get_font(20).render("15", True, "Black")
        TIME_PER_TURN_1_RECT = TIME_PER_TURN_1_TEXT.get_rect(topleft = (125, 575))
        SCREEN.blit(TIME_PER_TURN_1_TEXT, TIME_PER_TURN_1_RECT)
        
        TIME_PER_TURN_2_TEXT = get_font(20).render("30", True, "Black")
        TIME_PER_TURN_2_RECT = TIME_PER_TURN_2_TEXT.get_rect(topleft = (300, 575))
        SCREEN.blit(TIME_PER_TURN_2_TEXT, TIME_PER_TURN_2_RECT)
        
        TIME_PER_TURN_3_TEXT = get_font(20).render("45", True, "Black")
        TIME_PER_TURN_3_RECT = TIME_PER_TURN_3_TEXT.get_rect(topleft = (475, 575))
        SCREEN.blit(TIME_PER_TURN_3_TEXT, TIME_PER_TURN_3_RECT)
        
        SETTING_SAVE = Button(image=None, pos=(375, 700), 
                            text_input="SAVE", font=get_font(50), base_color=COLOR_LABEL, hovering_color="White")
        SETTING_SAVE.changeColor(SETTING_MOUSE_POS)
        SETTING_SAVE.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 100 <= event.pos[0] <= 100 + CHECKBOX.get_width() and 275 <= event.pos[1] <= 275 + CHECKBOX.get_height():
                    BOARD_SIZE = 1
                if 275 <= event.pos[0] <= 275 + CHECKBOX.get_width() and 275 <= event.pos[1] <= 275 + CHECKBOX.get_height():
                    BOARD_SIZE = 2
                if 450 <= event.pos[0] <= 450 + CHECKBOX.get_width() and 275 <= event.pos[1] <= 275 + CHECKBOX.get_height():
                    BOARD_SIZE = 3
                if 100 <= event.pos[0] <= 100 + CHECKBOX.get_width() and 425 <= event.pos[1] <= 425 + CHECKBOX.get_height():
                    FIRST_PLAYER = 1
                if 275 <= event.pos[0] <= 275 + CHECKBOX.get_width() and 425 <= event.pos[1] <= 425 + CHECKBOX.get_height():
                    FIRST_PLAYER = 2
                if 450 <= event.pos[0] <= 450 + CHECKBOX.get_width() and 425 <= event.pos[1] <= 425 + CHECKBOX.get_height():
                    FIRST_PLAYER = 3
                if 100 <= event.pos[0] <= 100 + CHECKBOX.get_width() and 575 <= event.pos[1] <= 575 + CHECKBOX.get_height():
                    TIME_PER_TURN = 1
                if 275 <= event.pos[0] <= 275 + CHECKBOX.get_width() and 575 <= event.pos[1] <= 575 + CHECKBOX.get_height():
                    TIME_PER_TURN = 2
                if 450 <= event.pos[0] <= 450 + CHECKBOX.get_width() and 575 <= event.pos[1] <= 575 + CHECKBOX.get_height():
                    TIME_PER_TURN = 3
                if SETTING_SAVE.checkForInput(SETTING_MOUSE_POS):
                    menu()
        draw_checkbox()
        pygame.display.update()

def contact():
    while True:
        SCREEN.fill(COLOR_BACKGROUND)

        CONTACT_MOUSE_POS = pygame.mouse.get_pos()
        
        CONTACT_TEXT = get_font(75).render("CONTACT", True, "#b68f40")
        CONTACT_RECT = CONTACT_TEXT.get_rect(center=(375, 100))
        SCREEN.blit(CONTACT_TEXT, CONTACT_RECT)
        
        MEMBER_TEXT = get_font(25).render("MEMBER:", True, "#b68f40")
        MEMBER_RECT = MEMBER_TEXT.get_rect(topleft = (50, 200))
        SCREEN.blit(MEMBER_TEXT, MEMBER_RECT)
        
        HUNG_TEXT = get_font(20).render("Nguyen Ngoc Hung - 211200941", True, "Black")
        HUNG_RECT = HUNG_TEXT.get_rect(topleft = (100, 250))
        SCREEN.blit(HUNG_TEXT, HUNG_RECT)
        
        KHAI_TEXT = get_font(20).render("Ngo Van Khai - 211200941", True, "Black")
        KHAI_RECT = KHAI_TEXT.get_rect(topleft = (100, 300))
        SCREEN.blit(KHAI_TEXT, KHAI_RECT)
        
        DAT_TEXT = get_font(20).render("Nguyen Tien Dat - 211200941", True, "Black")
        DAT_RECT = DAT_TEXT.get_rect(topleft = (100, 350))
        SCREEN.blit(DAT_TEXT, DAT_RECT)
        
        VERSION_TEXT = get_font(25).render("VERSION:", True, "#b68f40")
        VERSION_RECT = VERSION_TEXT.get_rect(topleft = (50, 400))
        SCREEN.blit(VERSION_TEXT, VERSION_RECT)
         
        VERSION_NUMNBER_TEXT = get_font(20).render("1.0", True, "Black")
        VERSION_NUMNBER_RECT = VERSION_NUMNBER_TEXT.get_rect(topleft = (100, 450))
        SCREEN.blit(VERSION_NUMNBER_TEXT, VERSION_NUMNBER_RECT)
        
        ALGORITHM_TEXT = get_font(25).render("AI ALGORITHM:", True, "#b68f40")
        ALGORITHM_RECT = ALGORITHM_TEXT.get_rect(topleft = (50, 500))
        SCREEN.blit(ALGORITHM_TEXT, ALGORITHM_RECT)
        
        MINIMAX_TEXT = get_font(20).render("Minimax Algorithm", True, "Black")
        MINIMAX_RECT = MINIMAX_TEXT.get_rect(topleft = (100, 550))
        SCREEN.blit(MINIMAX_TEXT, MINIMAX_RECT)
        
        BACK_BUTTON = Button(image=None, pos=(375, 700), 
                            text_input="BACK", font=get_font(50), base_color=COLOR_LABEL, hovering_color="White")
        BACK_BUTTON.changeColor(CONTACT_MOUSE_POS)
        BACK_BUTTON.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(CONTACT_MOUSE_POS):
                    menu()
                    
        pygame.display.update()

def menu():
    while True:
        
        SCREEN.fill(COLOR_BACKGROUND)
        
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(75).render("CONNECT4", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100))

        START_BUTTON = Button(image=pygame.image.load("image/Play Rect.png"), pos=(375, 250), 
                            text_input="START", font=get_font(50), base_color=COLOR_LABEL, hovering_color="White")
        SETTING_BUTTON = Button(image=pygame.image.load("image/Options Rect.png"), pos=(375, 375), 
                            text_input="SETTING", font=get_font(50), base_color=COLOR_LABEL, hovering_color="White")
        CONTACT_BUTTON = Button(image=pygame.image.load("image/Options Rect.png"), pos=(375, 500), 
                            text_input="CONTACT", font=get_font(50), base_color=COLOR_LABEL, hovering_color="White")
        EXIT_BUTTON = Button(image=pygame.image.load("image/Quit Rect.png"), pos=(375, 625), 
                            text_input="EXIT", font=get_font(50), base_color=COLOR_LABEL, hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [START_BUTTON, SETTING_BUTTON, CONTACT_BUTTON, EXIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if START_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if SETTING_BUTTON.checkForInput(MENU_MOUSE_POS):
                    setting()
                if CONTACT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    contact()
                if EXIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()
        
def main():
    menu()
    
if __name__ == "__main__":
    main()