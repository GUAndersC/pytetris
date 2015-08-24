import sys, pygame
import time

pygame.init()

screen = pygame.display.set_mode([640, 480])

block = pygame.image.load("Square.png")
background_block = pygame.image.load("SquareGray.png")

#rect = block.get_rect()

#block = pygame.Surface((16,16))

#block.fill((255,0,255))

BLOCKSIZE = 16

SCREEN_OFFSET_X = 240
SCREEN_OFFSET_Y = 80

rowsize = 640 / 16
colsize = 480 / 16

ROWS = 20
COLUMNS = 10

piece_T = ((0,0), (1,0), (-1,0), (0,1))
piece_L =   (
                ((0,0), (-1,0), (1,0), (1,1)),
                ((0,0), (0,-1), (0,1), (1,-1)),
                ((0,0), (1,0), (-1,0), (1,1))
            )

piece_square =   (
                ((0,0), (1,0), (0,1), (1,1)),
#                ((0,0), (0,-1), (0,1), (1,-1)),
#                ((0,0), (1,0), (-1,0), (1,1))
            )
def draw_board(board):
    for y, row in enumerate(board):
      for x, cell in enumerate(row):
        if cell:
            screen.blit(block, [BLOCKSIZE*x + SCREEN_OFFSET_X,BLOCKSIZE*y + SCREEN_OFFSET_Y])
        else:
            screen.blit(background_block, [BLOCKSIZE*x + SCREEN_OFFSET_X, BLOCKSIZE*y + SCREEN_OFFSET_Y])



def draw_piece(piece, piece_position):
    for block_position in piece:
        screen.blit(block,
                            [BLOCKSIZE*(block_position[0]+piece_position[0]) + SCREEN_OFFSET_X,
                            (BLOCKSIZE*(block_position[1]+piece_position[1]) + SCREEN_OFFSET_Y)
                            ]
                    )

def spawn_piece(state, piece, position):

    state["player_piece"] = piece
    state["player_position"] = position
    state["player_rotation"] = 0

def add_blocks_to_board(board, position, rotation, piece):

    for block in piece[rotation]:
        board[position[1]+block[1]][position[0]+block[0]] = 1

def remove_full_rows(state):
    board = state["board"]

    for i, row in enumerate(board):
        if all([block > 0 for block in row]):
            del board[i]
            board.insert(0, [0 for _ in range(0, COLUMNS)])

def game_update(state):

    state["total_time"] += state["dt"]

    if state["total_time"] > 1.0:
        state["player_position"][1] += 1

        if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]):
            state["player_position"][1] -= 1
            add_blocks_to_board(state["board"], state["player_position"], state["player_rotation"], state["player_piece"])
            remove_full_rows(state)
            spawn_piece(state, piece_square, [5,0])

        state["total_time"] -= 1.0



    screen.fill([0,0,0])

    player_position = state["player_position"]
    player_piece = state["player_piece"]
    player_rotation = state["player_rotation"]

    draw_board(state["board"])
    draw_piece(player_piece[player_rotation], player_position)

    pygame.display.flip()


def validate_move(board, position, rotation, piece):

    for coord in piece[rotation]:
        x = coord[0] + position[0]
        y = coord[1] + position[1]

        if (x >= COLUMNS or x < 0) or (y >= ROWS or y < 0):
            return False

        if board[y][x] != 0:
            return False

    return True

def game_handle_input(state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: sys.exit()

            elif event.key == pygame.K_UP:
                n_rotations = len(state["player_piece"])
                old_rotation = state["player_rotation"]
                state["player_rotation"] = (state["player_rotation"] + 1) % n_rotations
                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_rotation"] = old_rotation

            elif event.key == pygame.K_DOWN:
                state["player_position"][1] += 1
                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_position"][1] -= 1

            elif event.key == pygame.K_LEFT:
                state["player_position"][0] -= 1
                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_position"][0] += 1

            elif event.key == pygame.K_RIGHT:
                state["player_position"][0] += 1
                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_position"][0] -= 1

            elif event.key == pygame.K_SPACE:
                done = False
#                while not done:
                #TODO: Auto block falling etc.

def game_main():

    total_time = 0

    state = {

        "board": [[0 for x in range(0, COLUMNS)] for y in range(0, ROWS)],
        "dt": 0,
        "total_time": 0,
        "player_position": [5,0],
        "player_piece": piece_square,
        "player_rotation": 0,
    }

#    state["board"][9][19] = 1

    while 1:
        t = time.time()
        time.sleep(1/30)
        game_handle_input(state)
        game_update(state)
        state["dt"] = time.time() - t

game_main()
