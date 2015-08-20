import sys, pygame
import time

pygame.init()

screen = pygame.display.set_mode([640, 480])

block = pygame.image.load("Square.png")
#rect = block.get_rect()

#block = pygame.Surface((16,16))

#block.fill((255,0,255))

BLOCKSIZE = 16

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

def draw_board(board):
    for i, row in enumerate(board):
      for j, cell in enumerate(row):
        if cell:
            screen.blit(block, [BLOCKSIZE*i,BLOCKSIZE*j])



def draw_piece(piece, piece_position):
    for block_position in piece:
        screen.blit(block,
                            [BLOCKSIZE*(block_position[0]+piece_position[0]),
                            (BLOCKSIZE*(block_position[1]+piece_position[1]))
                            ]
                    )

def game_update(board, player):
    screen.fill([0,0,0])

    

    draw_board(board)
    draw_piece(player["piece"][player["rotation"]], player["position"])

    pygame.display.flip()


def validate_move(board, player):

    position = player["position"]

    for coord in player["piece"][player["rotation"]]:
        x = coord[0] + position[0]
        y = coord[1] + position[1]

        if (x >= COLUMNS or x < 0) or (y >= ROWS or y < 0):
            return False

        if board[x][y] != 0:
            return False

    return True

def game_loop(board, player, dt):

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: sys.exit()

            elif event.key == pygame.K_UP:
                n_rotations = len(player["piece"])
                old_rotation = player["rotation"]
                player["rotation"] = (player["rotation"] + 1) % n_rotations
                if not validate_move(board, player): player["rotation"] = old_rotation

            elif event.key == pygame.K_DOWN:
                player["position"][1] += 1
                if not validate_move(board, player): player["position"][1] -= 1

            elif event.key == pygame.K_LEFT:
                player["position"][0] -= 1
                if not validate_move(board, player): player["position"][0] += 1

            elif event.key == pygame.K_RIGHT:
                player["position"][0] += 1
                if not validate_move(board, player): player["position"][0] -= 1


    game_update(board, player, dt)



def game_main():

#    t = time.time()

    dt = 0

    board = [[0 for y in range(0, ROWS)] for x in range(0, COLUMNS)]

    board[5][5] = 1

    player =    {
                "position": [0,1],
                "piece": piece_L,
                "rotation": 0,
            }

    while 1:
        t = time.time()
        time.sleep(1/30)
        game_loop(board, player, dt)
        dt = time.time() - t

game_main()
