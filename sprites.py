from functools import lru_cache
from pathlib import Path

import pygame

IMAGES_DIR = Path(__file__).parent / 'images'
SHEET_NAME = 'fleet_elvira.png'
COLUMNS = 8  # frames de animação por linha


@lru_cache(maxsize=1)
def load_ship_families():
    """Carrega a sheet e devolve uma lista de designs.

    Cada design é uma lista de frames (uma linha da sheet).
    O lru_cache garante que a imagem é lida só uma vez.
    """
    sheet = pygame.image.load(IMAGES_DIR / SHEET_NAME).convert_alpha()
    frame_w = sheet.get_width() // COLUMNS
    frame_h = frame_w  # ajuste se os frames não forem quadrados
    rows = sheet.get_height() // frame_h

    designs = []
    for row in range(rows):
        frames = []
        for col in range(COLUMNS):
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            frames.append(sheet.subsurface(rect).copy())
        designs.append(frames)
    return designs