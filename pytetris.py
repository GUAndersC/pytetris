import sys, pygame, random
import time


#block.fill((0,220,0), None, pygame.BLEND_MULT)

#tint = pygame.Surface((16,16))
#tint.fill((0,50,0), pygame.BLEND_ADD)

#rect = block.get_rect()

#block = pygame.Surface((16,16))

#block.fill((255,0,255), None, pygame.BLEND_ADD)

BLOCKSIZE = 16

SCREEN_OFFSET_X = 240
SCREEN_OFFSET_Y = 80

rowsize = 640 / 16
colsize = 480 / 16

ROWS = 20
COLUMNS = 10

PIECES = [

        #T
        {
            "color": (0,220, 0),
            "rotations": (
                            ((-1,0), (0,0), (1,0), (2,0)),
                            ((0,-2), (0,-1), (0,0), (0,1)),
                        )
        },

        #L1
        {
            "color": (220, 0, 0),
            "rotations": (
                            ((-1,0), (0,0), (1,0), (-1,1)),
                            ((-1,-1), (0,-1), (0,0), (0,1)),
                            ((1,-1), (-1,0), (0,0), (1,0)),
                            ((0,-1), (0,0), (0,1), (1,1)),
                        ),
        },

        #L2
    #    {
    #        "color": (220, 0, 0),
    #        "rotations": (
    #                        ((-1,0), (0,0), (1,0), (-1,1)),
    #                        ((-1,-1), (0,-1), (0,0), (0,1)),
    #                        ((1,-1), (-1,0), (0,0), (1,0)),
    #                        ((0,-1), (0,0), (0,1), (1,1)),
    #                    ),
    #    },


        #S1
        {
            "color": (220, 0, 0),
            "rotations": (
                            ((0,-1), (1,-1), (-1,0), (0,0)),
                            ((0,-1), (0,0), (1,0), (1,1)),
                        ),
        },

        #S2
        {
            "color": (220, 0, 0),
            "rotations": (
                            ((-1,-1), (0,-1), (0,0), (1,0)),
                            ((1,-1), (0,0),(1,0),(0,1)),
                        ),
        },

        #Square
        {
            "color": (220, 0, 0),
            "rotations": (
                            ((0,0), (1,0), (0,1), (1,1)),
                            ((0,0), (1,0), (0,1), (1,1)),
                        ),
        },

    ]

def select_piece():
    return PIECES[random.randint(0, len(PIECES) - 1)]
#    return PIECES[2]

def draw_board(board):
    for y, row in enumerate(board):
      for x, cell in enumerate(row):
            new_block = block.copy()
            new_block.fill(board[y][x], None, pygame.BLEND_MULT)
            screen.blit(new_block, [BLOCKSIZE*x + SCREEN_OFFSET_X,BLOCKSIZE*y + SCREEN_OFFSET_Y])


def draw_piece(piece, piece_position, player_rotation):
    for block_position in piece["rotations"][player_rotation]:

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

    for block in piece["rotations"][rotation]:
        board[position[1]+block[1]][position[0]+block[0]] = piece["color"]

def remove_full_rows(state):
    board = state["board"]

    for i, row in enumerate(board):
        if all([block > 0 for block in row]):
            del board[i]
            board.insert(0, [0 for _ in range(0, COLUMNS)])

def try_drop_piece(state):
    state["player_position"][1] += 1

    if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]):
        state["player_position"][1] -= 1
        add_blocks_to_board(state["board"], state["player_position"], state["player_rotation"], state["player_piece"])
        remove_full_rows(state)
        spawn_piece(state, select_piece(), [5,0])

def game_update(state, dt):

    if not state["player_falling"]:
        state["total_time"] += dt


    if state["total_time"] > 1.0 and state["player_falling"] == False:
        try_drop_piece(state)
        state["total_time"] -= 1.0

    if state["player_falling"]:
        state["falling_timer"] += dt
        if state["falling_timer"] > 0.1:
            try_drop_piece(state)
            state["falling_timer"] -= 0.1

    screen.fill([0,0,0])

    player_position = state["player_position"]
    player_piece = state["player_piece"]
    player_rotation = state["player_rotation"]

    draw_board(state["board"])
    draw_piece(player_piece, player_position, player_rotation)

    pygame.display.flip()


def validate_move(board, position, rotation, piece):

    for coord in piece["rotations"][rotation]:
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
                state["player_falling"] = True
#                state["player_position"][1] += 1
#                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_position"][1] -= 1

            elif event.key == pygame.K_LEFT:
                state["player_position"][0] -= 1
                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_position"][0] += 1

            elif event.key == pygame.K_RIGHT:
                state["player_position"][0] += 1
                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_position"][0] -= 1

#            elif event.key == pygame.K_SPACE:
                #TODO: Implement

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                state["player_falling"] = False

def game_main():

    pygame.init()

    screen = pygame.display.set_mode([640, 480])

    block = pygame.image.load("Square.png")
    background_block = pygame.image.load("SquareGray.png")

    total_time = 0

    dt = 0

    state = {

        "board": [[(20,20,20) for x in range(0, COLUMNS)] for y in range(0, ROWS)],
        "total_time": 0,
        "player_position": [5,0],
        "player_piece": select_piece(),
        "player_rotation": 0,
        "player_falling": False,
        "falling_timer": 0.0,
    }

#    state["board"][9][19] = 1

    while 1:
        t = time.time()
        time.sleep(1/30)
        game_handle_input(state)
        game_update(state, dt)
        dt = time.time() - t

#for piece in PIECES:
#    print(piece)

if __name__ == "__main__":
    game_main()
