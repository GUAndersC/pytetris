import sys, pygame

screen = pygame.display.set_mode([640, 480])

blocksize = 16

rowsize = 640 / 16
colsize = 480 / 16


def draw_board(board):
    for i, row in enumerate(board):
      for j, cell in enumerate(row):
        if cell:
#            print(i*rowsize, j*colsize)
            screen.blit(block, [blocksize*i,blocksize*j])



def draw_piece(piece, piece_position):
    for block_position in piece:
        screen.blit(block,
                            [blocksize*(block_position[0]+piece_position[0]),
                            (blocksize*(block_position[1]+piece_position[1]))
                            ]
                    )

pygame.init()


block = pygame.image.load("Square.png")
rect = block.get_rect()

screen.fill([0,0,0])

grid = [[0 for x in range(0, 10)] for x in range(0, 20)]


piece_T = ((0,0), (1,0), (-1,0), (0,1))
piece_L = ((0,0), (-1,0), (1,0), (1,1))

player_position = (5,9)

#grid[0][1] = 1
#grid[0][0] = 1

draw_piece(piece_T, player_position)

draw_board(grid)

pygame.display.flip()
