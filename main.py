import pygame
import random

import math
import json
import urllib.request

from sys import exit

# config
window_width = 1280
window_height = 720

border_color = (49, 230, 59)
bg_color = (14, 4, 28)

CHAR_Land = '.,-~:;=+*#$@'
CHAR_Ocean = ' ..`.. '

border = 20
text_x = 40
text_gap = 16

# setup
pygame.init() 
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("CHARACTER DISPLAY")
clock = pygame.time.Clock()

font_small = pygame.font.Font("assets/fonts/SpaceMono-Regular.ttf", 14)
font_big = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf",60)

land_mask = pygame.image.load("assets/worldMap.jpg").convert()
land_w, land_h = land_mask.get_size()

# scanlines
def create_scanlines(size):
    surf = pygame.Surface(size).convert_alpha()
    surf.fill((0,0,0,0))

    for j in range(0, size[1], 4):
        surf.fill((0,0,0,40), (0, j, size[0], 1))

    return surf

SCANLINES = create_scanlines((window_width, window_height))

# land mask sampling
def check_land(lat,lon):
    px = int(((lon + 180)/360) * land_w) % land_w
    py = int(((90 - lat)/180) * land_h)
    px = max(0, min(land_w - 1, px))
    py = max(0, min(land_h - 1, py))
    colour = land_mask.get_at((px,py))
    r,g,b = colour.r, colour.g, colour.b
    return not ((b > r + 30) and (b > g + 10))

# latitude & longitude -> screen position
def project(lat, lon, cx, cy, radius, rotation):
    lat_r = math.radians(lat)
    lon_r = math.radians(lon + rotation)
    x = math.cos(lat_r) * math.sin(lon_r)
    y = math.sin(lat_r)
    z = math.cos(lat_r) * math.cos(lon_r)
    sx = cx + int(x * radius)
    sy = cy - int(y * radius)
    return sx,sy,x,y,z

# ascii globe 
def draw_globe(surface, font, cx, cy, radius, rotation):
    lx,ly,lz = 0.5, 0.4, 0.77
    cell_w = font.size("A")[0]
    cell_h = font.get_height()
    cols = surface.get_width() // cell_w
    rows = surface.get_height() // cell_h
    buf = {}
    zbuf = {}

    for lat in range(-90, 91, 2):
        for lon in range(0, 360, 2):
            sx, sy, x, y, z = project(lat, lon, cx, cy, radius, rotation)
            if z<0:
                continue
            
            col = sx // cell_w
            row = sy // cell_h

            if ((col < 0) or (col>=cols) or (row<0) or (row>=rows)):
                continue
            
            if (z > zbuf.get((col,row), -999)):
                zbuf[(col,row)] = z
                brightness = ((x * lx) + (y * ly) + (z * lz) + 1) / 2
                real_lon = (((lon - rotation) + 540) % 360) - 180
                land = check_land(lat, real_lon)

                if land:
                    char = CHAR_Land[int(brightness * (len(CHAR_Land) - 1))]
                    colour = (int(20 + brightness * 90), int(120 + brightness * 135), int(20 + brightness * 40))
                else:
                    char = CHAR_Ocean[int(brightness * (len(CHAR_Ocean) - 1))]
                    colour = (int(40 + brightness * 40), int(120 + brightness * 80), int(200 + brightness * 55))

                buf[(col, row)] = (char,colour)
    
    # render buffer to surface
    for ((col,row), (char,colour)) in buf.items():
        glyph = font.render(char, True, colour)
        surface.blit(glyph, ((col * cell_w), (row * cell_h)))
                    
rotation = 0

# main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # bg & overlay
    window.fill(bg_color)
    window.blit(SCANLINES, (0, 0))

    # border text
    topline = font_small.render("HRKRN.BUILD / PROJECTS/", True, border_color)
    text_width = topline.get_width()

    # frame
    pygame.draw.line(window, border_color, (border, border), (text_x - text_gap, border), 1)
    pygame.draw.line(window, border_color, (text_x + text_width + text_gap, border), (window_width - border, border), 1)
    pygame.draw.line(window, border_color, (border, border), (border, window_height - border), 1)
    pygame.draw.line(window, border_color, (window_width - border, border), (window_width - border, window_height - border), 1)
    pygame.draw.line(window, border_color, (border, window_height - border), (window_width - border, window_height - border), 1)

    window.blit(topline, (text_x, border - 9))

    # big text
    title_text = font_big.render("PLANET EARTH", True, border_color)
    text_width = topline.get_width()

    window.blit(title_text, (text_x + 5, 620))

    # ASCII globe
    draw_globe(window, font_small, (window_width // 2), (window_height // 2), 200, rotation)
    rotation += 0.3

    # glitch lines
    if random.randint(0, 120) == 0:
        for _ in range(random.randint(1, 5)):
            y = random.randint(0, window_height)
            offset = random.randint(2, 10)
            pygame.draw.rect(window, (60, 55, 80), (offset, y, window_width, 1))

    pygame.display.update()
    clock.tick(60)