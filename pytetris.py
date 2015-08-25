import sys, pygame, random
import time

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
            "color": (0, 0, 220),
            "rotations": (
                            ((0,-1), (1,-1), (-1,0), (0,0)),
                            ((0,-1), (0,0), (1,0), (1,1)),
                        ),
        },

        #S2
        {
            "color": (220, 0, 220),
            "rotations": (
                            ((-1,-1), (0,-1), (0,0), (1,0)),
                            ((1,-1), (0,0),(1,0),(0,1)),
                        ),
        },

        #Square
        {
            "color": (220, 220, 0),
            "rotations": (
                            ((0,0), (1,0), (0,1), (1,1)),
                            ((0,0), (1,0), (0,1), (1,1)),
                        ),
        },

    ]

def select_piece():
    """ :: -> Piece
    Returns a random piece. """
    return PIECES[random.randint(0, len(PIECES) - 1)]

def draw_board(screen, block_sprite, board):
    """ :: Surface -> Sprite -> Board -> ()
    Draws the board using the sprite on the surface. """
    for y, row in enumerate(board):
      for x, cell in enumerate(row):
            # TODO: block is global
            new_block = block_sprite.copy()
            new_block.fill(board[y][x], None, pygame.BLEND_MULT)
            screen.blit(new_block, [BLOCKSIZE*x + SCREEN_OFFSET_X,BLOCKSIZE*y + SCREEN_OFFSET_Y])


def draw_piece(screen, block_sprite, piece, piece_position, player_rotation):
    """ :: Surface -> Sprite -> Piece -> Position -> Rotation -> ()
    Draws the piece, using the sprite, at the position,
    using the rotation, on the surface. """

    new_block = block_sprite.copy()
    new_block.fill(piece["color"], None, pygame.BLEND_MULT)

    for block_position in piece["rotations"][player_rotation]:
        screen.blit(new_block,
                            [BLOCKSIZE*(block_position[0]+piece_position[0]) + SCREEN_OFFSET_X,
                            (BLOCKSIZE*(block_position[1]+piece_position[1]) + SCREEN_OFFSET_Y)
                            ]
                    )

def spawn_piece(state, piece, position):
    """ :: GameState -> Piece -> Vector -> ()
    Adds the specified piece to the game state at the specified position"""

    state["player_piece"] = piece
    state["player_position"] = position
    state["player_rotation"] = 0

def add_blocks_to_board(state):
    """ :: GameState -> ()
    Adds player piece to board. """
    board = state["board"]
    position = state["player_position"]
    rotation = state["player_rotation"]
    piece = state["player_piece"]

    for block in piece["rotations"][rotation]:
        board[position[1]+block[1]][position[0]+block[0]] = piece["color"]

def remove_full_rows(state):
    """ :: GameState -> ()
    Removes full rows in board TODO: and grants user some points. """
    board = state["board"]

    for i, row in enumerate(board):
        if all([block > 0 for block in row]):
            del board[i]
            board.insert(0, [(20,20,20) for _ in range(0, COLUMNS)])

def try_drop_piece(state):
    """ :: GameState -> ()
    Move player piece down one step if possible. """

    state["player_position"][1] += 1

    if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]):
        state["player_position"][1] -= 1
        add_blocks_to_board(state)
        remove_full_rows(state)
        spawn_piece(state, select_piece(), [5,0])

def game_update(state, dt):
    """ :: GameState -> TimeDelta -> ()
    Updates game state based on game rules (Does "physics") """

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


def game_draw(screen, block_sprite, state):
    """ :: ScreenSurface -> Sprite -> GameState -> ()
    Draws game onto screen """
    screen.fill([0,0,0])

    player_position = state["player_position"]
    player_piece = state["player_piece"]
    player_rotation = state["player_rotation"]

    draw_board(screen, block_sprite, state["board"])
    draw_piece(screen, block_sprite, player_piece, player_position, player_rotation)

    pygame.display.flip()


def validate_move(board, position, rotation, piece):
    """ :: Board -> Position -> Rotation -> Piece -> Boolean
    Is current state of the board valid? """

    for coord in piece["rotations"][rotation]:
        x = coord[0] + position[0]
        y = coord[1] + position[1]

        if (x >= COLUMNS or x < 0) or (y >= ROWS or y < 0):
            return False

        if board[y][x] != (20,20,20):
            return False

    return True

def game_handle_input(state):
    """ :: GameState -> ()
    Handles user input """

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

            elif event.key == pygame.K_LEFT:
                state["player_position"][0] -= 1
                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_position"][0] += 1

            elif event.key == pygame.K_RIGHT:
                state["player_position"][0] += 1
                if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]): state["player_position"][0] -= 1

            elif event.key == pygame.K_SPACE:
                pass

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                state["player_falling"] = False

def game_main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode([640, 480])

    # Textures
    block = pygame.image.load("Square.png")

    # Time management
    total_time = 0
    dt = 0

    # Game state
    state = {
        "board": [[(20,20,20) for x in range(0, COLUMNS)] for y in range(0, ROWS)],
        "total_time": 0,
        "player_position": [5,0],
        "player_piece": select_piece(),
        "player_rotation": 0,
        "player_falling": False,
        "falling_timer": 0.0,
    }

    # Game loop
    while 1:
        t = time.time()
        time.sleep(1/30)
        game_handle_input(state)
        game_update(state, dt)
        game_draw(screen, block, state)
        dt = time.time() - t

if __name__ == "__main__":
    game_main()
