import pygame
from pygame.constants import GL_RED_SIZE
import pygame.freetype
import random
import os
import sys 
import time

s_width = 515
s_height = 660
play_width = 300
play_height = 600
block_size = 30

windowX = 100
windowY = 200
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (windowX,windowY)

pygame.init()
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Tetris")

pygame.font.init() 

top_left_x = 30
top_left_y = 30
 

S = [
    ["00000", "000000", "001100", "011000", "00000"],
    ["00000", "00100", "00110", "00010", "00000"],
]

Z = [
    ["00000", "00000", "01100", "00110", "00000"],
    ["00000", "00100", "01100", "01000", "00000"],
]

I = [
    ["00100", "00100", "00100", "00100", "00000"],
    ["00000", "11110", "00000", "00000", "00000"],
]

O = [["00000", "00000", "01100", "01100", "00000"]]

J = [
    ["00000", "01000", "01110", "00000", "00000"],
    ["00000", "00110", "00100", "00100", "00000"],
    ["00000", "00000", "01110", "00010", "00000"],
    ["00000", "00100", "00100", "01100", "00000"],
]

L = [
    ["00000", "00010", "01110", "00000", "00000"],
    ["00000", "00100", "00100", "00110", "00000"],
    ["00000", "00000", "01110", "01000", "00000"],
    ["00000", "01100", "00100", "00100", "00000"],
]

T = [
    ["00000", "00100", "01110", "00000", "00000"],
    ["00000", "00100", "00110", "00100", "00000"],
    ["00000", "00000", "01110", "00100", "00000"],
    ["00000", "00100", "01100", "00100", "00000"],
]

 
shapes = [I, J, L, O, S, T, Z]
shape_colors = [(1, 240, 241), (1, 1, 240), (239, 160, 0), (240, 240, 1), (0, 240, 0), (160, 0, 241), (240, 1, 0)]


 
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


class Tetris(object):
    def __init__(self, win):
        self.locked_positions = {}
        self.grid = self.create_grid()
        self.change_piece = False
        self.current_piece = self.generate_shape()
        self.next_piece = self.generate_shape()
        
        self.clock = pygame.time.Clock()
        
        self.fall_time = 0
        self.level = 0
        self.lines = 0
        self.score = 0
        
        self.keys_pressed = [False, False, False] # left, right, down
        self.key_down_time = [0, 0, 0]
        self.das = False
        self.frame_das_start = 16
        self.frame_das = 6
        
        self.frame_rate = 60
        self.total_frames = 0
                
        self.run = True
        
        self.level_speeds = [
            18, # 0
            18, # 1
            18, # 2
            18, # 3
            18, # 4
            18, # 5
            18, # 6
            13, # 7
            8,  # 8
            6,  # 9
            5,  # 10
            5,  # -
            5,  # 12
            4,  # 13
            4,  # -
            4,  # 15
            3,  # 16
            3,  # -
            3,  # 18
            2,  # 19
            2,
            2,
            2,
            2,  # -
            2,
            2,
            2,
            2,
            2,  # 28
            1
        ]
        self.speed = self.level_speeds[self.level]

        self.pause = False

        self.surface = win
        self.renderer = Renderer(win, self)
    
    def update_grid(self):
        shape_pos = self.convert_shape_format(self.current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                self.grid[y][x] = self.current_piece.color
        
        if self.change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                self.locked_positions[p] = self.current_piece.color
            self.current_piece = self.next_piece
            self.next_piece = self.generate_shape()
            self.change_piece = False
            if self.check_game_over():
                self.run = False
            self.clear_rows()
    
    def get_keys(self):
        print(self.das)
        game_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN]
        
        if self.pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                            self.pause = False
            return
        else:
            
            if True in self.keys_pressed:
                for i, key in enumerate(self.keys_pressed):
                    if key:
                        self.key_down_time[i] += 1
                    if self.das:
                        if self.key_down_time[i] >= self.frame_das:
                            x = [-1, 1, 0][i]
                            y = [0, 0, 1][i]
                            self.move_cur_piece(x, y)
                            if not self.valid_space(self.current_piece):
                                self.move_cur_piece(x=-x, y=-y)
                                self.das = False
                            self.key_down_time[i] = 0
                    elif self.key_down_time[i] >= self.frame_das_start:
                        self.das = True
                        x = [-1, 1, 0][i]
                        y = [0, 0, 1][i]
                        self.move_cur_piece(x, y)
                        if not self.valid_space(self.current_piece):
                                self.move_cur_piece(x=-x, y=-y)
                                self.das = False
                        self.key_down_time[i] = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if not self.change_piece:
                        
                        if event.key == pygame.K_LEFT:
                            self.move_cur_piece(x=-1)
                            if not self.valid_space(self.current_piece):
                                self.move_cur_piece(x=1)
                        if event.key == pygame.K_RIGHT:
                            self.move_cur_piece(x=1)
                            if not self.valid_space(self.current_piece):
                                self.move_cur_piece(x=-1)
                        if event.key == pygame.K_DOWN:
                            self.move_cur_piece(y=1)
                            if not self.valid_space(self.current_piece):
                                self.move_cur_piece(y=-1)
                        
                        if event.key == pygame.K_SPACE:
                            self.current_piece.rotation += 1
                            if not self.valid_space(self.current_piece):
                                self.current_piece.rotation -= 1
                        if event.key == pygame.K_RETURN:
                            while self.valid_space(self.current_piece):
                                self.move_cur_piece(y=1)
                            self.move_cur_piece(y=-1)
                            self.change_piece = True
                        
                        # DAS
                        if event.key in game_keys:
                            ind = game_keys.index(event.key)
                            self.keys_pressed[ind] = True
                            self.key_down_time[ind] = 1
                        
                    # PAUSE
                    if event.key == pygame.K_ESCAPE:
                        self.pause = True
                if event.type == pygame.KEYUP:
                    if event.key in game_keys:
                        self.das = False
                        self.keys_pressed[game_keys.index(event.key)] = False
                        
    def render_frames(self):
        font = pygame.font.Font("font.ttf", 30)
        label = font.render(str(self.total_frames % self.frame_rate), False, (255, 255, 255))
        self.surface.blit(label, (0, 0))
    
    def predictTyle(self, shape):
        temp = Piece(shape.x, shape.y, shape.shape)
        temp.rotation = shape.rotation

        # self.printArray(self.grid)
        
        while self.valid_space(temp):
            temp.y += 1
        temp.y -= 1
        format = shape.shape[shape.rotation % len(shape.shape)]

        sx, sy = top_left_x, top_left_y

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == "1":
                    self.renderer.renderPiece(sx + (temp.x * block_size) + (j - 2) * block_size, sy + (temp.y * block_size) + (i - 4) * block_size, (128, 128, 128), border=True)
    
    def move_cur_piece(self, x=0, y=0):
        self.current_piece.x += x
        self.current_piece.y += y
    
    def render(self):
        self.renderer.render(self.grid, self.next_piece, self.score, self.level, self.current_piece)
        # self.render_frames()
    
    def frame(self):
        
        self.total_frames += 1
        
        self.fall_time += self.clock.get_rawtime()
        self.update_speed()
        self.clock.tick(self.frame_rate)
        
        if self.fall_time / 1000 >  self.speed / 60:
            self.fall_time = 0
            self.move_cur_piece(y=1)
            if not self.valid_space(self.current_piece) and self.current_piece.y > 0:
                self.move_cur_piece(y=-1)
                self.change_piece = True

    def update_speed(self):
        if self.level < 29:
            self.speed = self.level_speeds[self.level]
        else:
            self.speed = 1
    
    def check_new_level(self):
        if self.lines >= 10:
            self.level += 1
            self.lines = 0

    def create_grid(self):
        grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in self.locked_positions:
                    key = self.locked_positions[(j, i)]
                    grid[i][j] = key

        self.grid = grid

    def generate_shape(self):
        return Piece(5, 0, random.choice(shapes))

    def convert_shape_format(self, shape):
        positions = []
        format = shape.shape[shape.rotation % len(shape.shape)]
    
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '1':
                    positions.append((shape.x + j, shape.y + i))
    
        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)
    
        return positions

    def valid_space(self, piece):
        accepted_positions = [[(j, i) for j in range(10) if self.grid[i][j] == (0,0,0)] for i in range(20)]
        accepted_positions = [j for sub in accepted_positions for j in sub]
        formatted = self.convert_shape_format(piece)
        
        for pos in formatted:
            if pos not in accepted_positions:
                if pos[1] > -1:
                    return False
    
        return True

    def check_game_over(self):
        for pos in self.locked_positions:
            x, y = pos
            if y < 1:
                return True
        return False

    def clear_rows(self):
        inc = 0
                
        for i in range(len(self.grid)-1,-1,-1):
            row = self.grid[i]
            if (0, 0, 0) not in row:
                inc += 1
                ind = i
                                        
        if inc > 0:
            whiteScreen = False
            clearInd = [[4, 5], [3, 6], [2, 7], [1, 8], [0, 9]]
            for arr in clearInd:
                self.surface.fill((0, 0, 0))
                if inc == 4:
                    if whiteScreen:
                        pygame.draw.rect(self.surface, (255, 255, 255), (top_left_x, top_left_y, play_width, play_height))
                        whiteScreen = False
                    else:
                        whiteScreen = True
                
                for j in arr:
                    for yInc in range(inc):
                        try:
                            self.grid[ind + yInc][j] = (0, 0, 0)
                            del self.locked_positions[(j, ind + yInc)]
                        except:
                            pass
                
                self.create_grid()
                self.update_grid()
                
                self.render()
                self.renderer.update()

                pygame.time.wait(50)
            
            pygame.time.wait(200)
            
            self.lines += inc
            if inc == 1:
                self.score += 40 * (self.level + 1)
            if inc == 2:
                self.score += 100 * (self.level + 1)
            if inc == 3:
                self.score += 300 * (self.level + 1)
            if inc == 4:
                self.score += 1200 * (self.level + 1)
            for key in sorted(list(self.locked_positions), key=lambda x: x[1])[::-1]:
                x, y = key
                if y < ind:
                    newKey = (x, y + inc)
                    self.locked_positions[newKey] = self.locked_positions.pop(key)
        self.check_new_level()

    def printArray(self, arr):
        s = [[str(e) for e in row] for row in arr]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        print('\n'.join(table))

    
class Renderer(object):
    def __init__(self, win, game):
        self.surface = win
        self.game = game

    def render(self, grid, next_shape, score, level, current_piece):
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] != (0, 0, 0):
                    blockX = top_left_x + j * block_size
                    blockY = top_left_y + i * block_size
                    self.renderPiece(blockX, blockY, grid[i][j])

        
        self.draw_next_shape(next_shape)
        self.dispGameInfo(score, level)
        
        if self.game.pause:
            self.draw_text_middle("PAUSE", 60, (255, 255, 255))
        
        pygame.draw.rect(self.surface, (128, 128, 128), (top_left_x, top_left_y, play_width, play_height), 4)
    
    def draw_text_middle(self, text, size, color):
        font = pygame.font.Font("font.ttf", size)
        label = font.render(text, False, color)
        self.surface.blit(label, (top_left_x + play_width/2 - label.get_width() / 2, top_left_y + play_height / 2 - label.get_height() / 2))

    def draw_next_shape(self, shape):
        top_right_x = top_left_x + play_width
        row_width = s_width - top_right_x

        pygame.font.init()

        font = pygame.font.Font('font.ttf', 28)
        label = font.render("Next Piece", False, (255, 255, 255))
        self.surface.blit(label, (top_right_x + row_width/2 - label.get_width() / 2, top_left_y))

        box_size = 90

        pygame.draw.rect(self.surface, (128, 128, 128), (top_right_x + row_width / 2 - box_size / 2, top_left_y + 35, box_size, box_size), 3)
        
        tyleW, tyleH, tyleStartX, tyleStartY = self.tyleInfo(shape)

        box_size = 60

        maxWH = max(tyleW, tyleH)
        tyle_size = box_size / maxWH

        sx = top_right_x + row_width / 2 - box_size / 2
        sy = top_left_y + 50


        # pygame.draw.rect(surface, (255, 255, 255), (sx, sy, box_size, box_size), 4)

        format = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == "1":
                    self.renderPiece(sx + (j - tyleStartX + (maxWH - tyleW) / 2) * tyle_size, sy + (i - tyleStartY + (maxWH - tyleH) / 2) * tyle_size, shape.color, tyle_size)

    def draw_grid(self, grid):
        sx = top_left_x
        sy = top_left_y

        for i in range(len(grid)):
            pygame.draw.line(self.surface, (128, 128, 128), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
            for j in range(len(grid[i])):
                pygame.draw.line(self.surface, (128, 128, 128), (sx + j * block_size, sy), (sx + j * block_size, sy + play_height))
    
    def renderPiece(self, x, y, color, size=30, border=False):
        if border:
            pygame.draw.rect(self.surface, color, (x, y, size, size), 2)
            return
        pygame.draw.rect(self.surface, color, (x, y, size, size))
        pygame.draw.rect(self.surface, (0, 0, 0), (x, y, size, size), 2)
        pygame.draw.line(self.surface, (255, 255, 255), (x + 4, y + 4),  (x + 8, y + 4), 3)
        pygame.draw.line(self.surface, (255, 255, 255), (x + 4, y + 4),  (x + 4, y + 8), 3)
        pygame.draw.rect(self.surface, (255, 255, 255), (x, y, 3, 3))

    def tyleInfo(self, tyle):
        grid = tyle.shape[tyle.rotation % len(tyle.shape)]

        minX, maxX, minY, maxY = len(grid[0]), 0, len(grid), 0

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] == "1":
                    minX = min(minX, j)
                    maxX = max(maxX, j)
                    minY = min(minY, i)
                    maxY = max(maxY, i)
        
        width = (maxX - minX) + 1
        height = (maxY - minY) + 1
        
        return width, height, minX, minY

    def dispGameInfo(self, score, level):
        top_right_x = top_left_x + play_width
        row_width = s_width - top_right_x
        font = pygame.font.Font('font.ttf', 35)
        
        labelTitleScore = font.render(f"Score", False, (255, 255, 255))
        self.surface.blit(labelTitleScore, (top_right_x + 25, top_left_y + 150))
        
        labelScore = font.render(str(score), False, (255, 255, 255))
        self.surface.blit(labelScore, (top_right_x + 25, top_left_y + 183))
        
        
        labelTitleLevel = font.render(f"Level", False, (255, 255, 255))
        self.surface.blit(labelTitleLevel, (top_right_x + 25, top_left_y + 220))
        
        labelLevel = font.render(str(level), False, (255, 255, 255))
        self.surface.blit(labelLevel, (top_right_x + 25, top_left_y + 253))

    def update(self):
        pygame.display.flip()

def main(surface):
    Game = Tetris(surface)

    while Game.run:
        surface.fill((0, 0, 0))
        
        Game.create_grid()
        if not Game.pause:
            Game.frame()
        Game.get_keys()
                
        Game.predictTyle(Game.current_piece)
        
        Game.update_grid()

        Game.render()
        Game.renderer.update()

def main_menu(surface):
    run = True
    clock = pygame.time.Clock()
    
    inc = 0
    time_passed = 0
    
    colors = [(216, 23, 24), (246, 156, 16), (212, 186, 15), (92, 192, 31), (53, 172, 255), (149, 45, 216)]
    letters = list("Tetris")
    
    while run:
        
        surface.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(surface)

        pygame.font.init()

        font = pygame.font.Font("font.ttf", 80)
        smallFont = pygame.font.Font("font.ttf", 24)
        
        if time_passed > 200:
            inc += 1
            time_passed = 0
        
        time_passed += clock.get_rawtime()
        clock.tick(60)

        for i, letter in enumerate(letters):
            letterLabel = font.render(letter, False, colors[(i - inc) % len(colors)])
            surface.blit(letterLabel, (110 + i * 50, 200))
        
        explain = smallFont.render("Press  any  key  to  start  the  game", False, (255, 255, 255))
        surface.blit(explain, (s_width/2 - explain.get_width() / 2, 500))
        
    
        pygame.display.flip()

 
main(win)