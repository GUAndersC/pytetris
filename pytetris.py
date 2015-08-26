import sys, pygame, random
import time

BLOCKSIZE = 16
SCREEN_OFFSET_X = 240
SCREEN_OFFSET_Y = 80
rowsize = 640 / 16
colsize = 480 / 16
ROWS = 20
COLUMNS = 10

ROWS_PER_LEVEL = 10

GAME_SPEED = 1.0

SCORES = (0, 40, 100, 300, 1200)

PIECES = [

        # I-shape
        {
            "color": (0, 220, 220),
            "rotations": (
                            ((-1,0), (0,0), (1,0), (2,0)),
                            ((0,-1), (0,0), (0,1), (0,2)),
                         ),
        },

        # J-shape
        {
            "color": (0, 0, 220),
            "rotations": (
                            ((-1,0), (0,0), (1,0), (1,1)),
                            ((0,-1), (0,0), (0,1), (-1,1)),
                            ((1,0), (0,0), (-1,0), (-1,-1)),
                            ((0,1), (0,0), (0,-1), (1,-1)),
                        ),
        },

        # L-shape
        {
            "color": (220, 100, 0),
            "rotations": (
                            ((-1,0), (0,0), (1,0), (-1,1)),
                            ((0,-1), (0,0), (0,1), (-1,-1)),
                            ((1,0), (0,0), (-1,0), (1,-1)),
                            ((0,1), (0,0), (0,-1), (1,1)),
                        ),
        },

        # O-shape
        {
            "color": (220, 220, 0),
            "rotations": (
                            ((-1,-1), (0,-1), (-1,0), (0,0)),
                         ),
        },

        # S-shape
        {
            "color": (0, 220, 0),
            "rotations": (
                            ((0,-1), (1,-1), (-1,0), (0,0)),
                            ((1,0), (1,1), (0,-1), (0,0)),
                         ),
        },

        # T-shape
        {
            "color": (200, 0, 150),
            "rotations": (
                            ((-1,0), (0,0), (1,0), (0,1)),
                            ((0,-1), (0,0), (0,1), (-1,0)),
                            ((1,0), (0,0), (-1,0), (0,-1)),
                            ((0,1), (0,0), (0,-1), (1,0)),
                         ),
        },

        # Z-shape
        {
            "color": (220, 0, 0),
            "rotations": (
                            ((-1,-1), (0,-1), (0,0), (1,0)),
                            ((1,-1), (1,0), (0,0), (0,1)),
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
        if(block_position[1]+piece_position[1] >= 0):
            screen.blit(new_block,
                                [BLOCKSIZE*(block_position[0]+piece_position[0]) + SCREEN_OFFSET_X,
                                (BLOCKSIZE*(block_position[1]+piece_position[1]) + SCREEN_OFFSET_Y)
                                ]
                        )

def spawn_piece(state, piece, position):
    """ :: GameState -> Piece -> Vector -> ()
    Adds the specified piece to the game state at the specified position"""

    board = state["board"]

    state["player_piece"] = piece
    state["player_position"] = position
    state["player_rotation"] = 0

    if not validate_move(board, position, 0, piece):
        state["playing"] = False

def add_blocks_to_board(state):
    """ :: GameState -> ()
    Adds player piece to board. """
    board = state["board"]
    position = state["player_position"]
    rotation = state["player_rotation"]
    piece = state["player_piece"]

    for block in piece["rotations"][rotation]:
        x = position[0]+block[0]
        y = position[1]+block[1]

        if x >= 0 and y >= 0:
            board[y][x] = piece["color"]

def calculate_score(rows, state):
    score_index = max(min(rows, 4), 0)

    state["score"] += SCORES[score_index] * (state["level"] + 1)

def remove_full_rows(state):
    """ :: GameState -> ()
    Removes full rows in board TODO: and grants user some points. """
    board = state["board"]

    rows_removed = 0

    for i, row in enumerate(board):
        if all([block != (20, 20, 20) for block in row]):
            del board[i]
            board.insert(0, [(20,20,20) for _ in range(0, COLUMNS)])
            rows_removed += 1


    state["row_count"] += rows_removed
    calculate_score(rows_removed, state)

def try_drop_piece(state):
    """ :: GameState -> ()
    Move player piece down one step if possible. """

    state["player_position"][1] += 1

    if not validate_move(state["board"], state["player_position"], state["player_rotation"], state["player_piece"]):
        state["player_position"][1] -= 1
        return False

    return True

def try_drop_piece_and_remove(state):
    if not try_drop_piece(state):
        add_blocks_to_board(state)
        remove_full_rows(state)
        spawn_piece(state, select_piece(), [5,0])

def game_update(state, dt):
    """ :: GameState -> TimeDelta -> ()
    Updates game state based on game rules (Does "physics") """

    if not state["player_falling"]:
        state["total_time"] += dt

    if state["total_time"] > (GAME_SPEED * state["speed_multiplier"]) and state["player_falling"] == False:
        try_drop_piece_and_remove(state)
        state["total_time"] -= GAME_SPEED * state["speed_multiplier"]

    while state["player_dropping"]:
        if not try_drop_piece(state):
            state["player_dropping"] = False
            add_blocks_to_board(state)
            remove_full_rows(state)
            spawn_piece(state, select_piece(), [5,0])

    if state["player_falling"]:
        state["falling_timer"] += dt
        if state["falling_timer"] > 0.1:
            try_drop_piece_and_remove(state)
            state["falling_timer"] -= 0.1

    if state["row_count"] >= ROWS_PER_LEVEL:
        state["row_count"] -= ROWS_PER_LEVEL
        state["level"] += 1
        state["speed_multiplier"] *= 0.8


def game_draw(screen, block_sprite, state):
    """ :: ScreenSurface -> Sprite -> GameState -> ()
    Draws game onto screen """
    screen.fill([0,0,0])

    player_position = state["player_position"]
    player_piece = state["player_piece"]
    player_rotation = state["player_rotation"]

    draw_board(screen, block_sprite, state["board"])
    draw_piece(screen, block_sprite, player_piece, player_position, player_rotation)

def validate_move(board, position, rotation, piece):
    """ :: Board -> Position -> Rotation -> Piece -> Boolean
    Is current state of the board valid? """
    for coord in piece["rotations"][rotation]:
        x = coord[0] + position[0]
        y = coord[1] + position[1]

        if (x >= COLUMNS or x < 0) or (y >= ROWS): #or y < 0):
            return False

        if y >= 0 and x >= 0 and board[y][x] != (20,20,20):
            return False

    return True

def game_handle_input(state):
    """ :: GameState -> ()
    Handles user input """

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: state["playing"] = False

            elif event.key == pygame.K_UP:
                n_rotations = len(state["player_piece"]["rotations"])
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
                state["player_dropping"] = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                state["player_falling"] = False

def game_main(screen):
    game_font = pygame.font.Font(None, 18)

    # Textures
    block = pygame.image.load("Square.png")

    # Time management
    total_time = 0
    dt = 0

    # Game state
    state = {

        "playing": True,
        "board": [[(20,20,20) for x in range(0, COLUMNS)] for y in range(0, ROWS)],
        "total_time": 0,
        "player_position": [5,0],
        "player_piece": select_piece(),
        "player_rotation": 0,
        "player_falling": False,
        "player_dropping": False,
        "falling_timer": 0.0,

        "row_count": 0,

        "level": 0,

        "speed_multiplier": 1.0,

        "score": 0,
    }

    # Game loop
    while state["playing"]:
        score_text = "Score: " + str(state["score"])
        level_text = "Level: " + str(state["level"])
        score_label = game_font.render(score_text, 1, (255,0,255))
        level_label = game_font.render(level_text, 1, (255, 0, 255))
        t = time.time()
        time.sleep(1/30)
        game_handle_input(state)

        game_update(state, dt)
        game_draw(screen, block, state)
        screen.blit(score_label, (420, 100))
        screen.blit(level_label, (420, 84))
        pygame.display.flip()
        dt = time.time() - t


def menu_screen(text, screen):

    font = pygame.font.Font(None, 30)

    while True:

        text_label = font.render(text, 1, (255, 0, 255))

        screen.blit(text_label, (180, 170))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: sys.exit()

                return


def game():

     # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode([640, 480])

    menu_screen("PRESS KEY TO START", screen)

    while True:
        game_main(screen)
        menu_screen("GAME OVER - Press key to try again", screen)

if __name__ == "__main__":
    game()
