from functools import lru_cache
from pathlib import Path

import pygame

IMAGES_DIR = Path(__file__).parent / 'images'
SHEET_NAME = 'fleet_elvira.png'
COLUMNS = 8  # frames de animação por linha

# Fator de aumento das naves.
SHIP_SCALE = 1.5

# Pixels com transparência abaixo deste valor são ignorados (sombras e resíduos).
ALPHA_MIN = 60


@lru_cache(maxsize=1)
def load_ship_families():
    """Carrega a sheet e devolve só os designs que têm nave visível.

    Cada design é uma lista de frames com o mesmo tamanho.
    """
    sheet = pygame.image.load(IMAGES_DIR / SHEET_NAME).convert_alpha()

    designs = []
    for band_y0, band_y1 in _find_bands(sheet):
        rects = _find_frames(sheet, band_y0, band_y1)
        design = _build_design(sheet, rects)
        if design is not None:
            designs.append(design)
    return designs


def _runs(flags, min_length=1):
    """Devolve os trechos contínuos de True como pares (início, fim)."""
    runs, start = [], None
    for i, flag in enumerate(flags + [False]):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            if i - start >= min_length:
                runs.append((start, i))
            start = None
    return runs


def _is_solid(sheet, x, y):
    """Retorna True se o pixel tem visibilidade suficiente."""
    return sheet.get_at((x, y)).a >= ALPHA_MIN


def _find_bands(sheet):
    """Acha as faixas horizontais de cada linha de naves."""
    w, h = sheet.get_size()
    row_has_ship = [
        any(_is_solid(sheet, x, y) for x in range(w)) for y in range(h)
    ]
    return _runs(row_has_ship, min_length=4)


def _find_frames(sheet, y0, y1):
    """Acha os frames de uma linha pelas colunas vazias entre eles."""
    w = sheet.get_width()
    col_has_ship = [
        any(_is_solid(sheet, x, y) for y in range(y0, y1)) for x in range(w)
    ]
    runs = _runs(col_has_ship, min_length=4)

    # Se não encontrar exatamente COLUMNS naves, divide a faixa em partes iguais.
    if len(runs) != COLUMNS:
        step = w / COLUMNS
        runs = [(round(i * step), round((i + 1) * step)) for i in range(COLUMNS)]

    return [pygame.Rect(x0, y0, x1 - x0, y1 - y0) for x0, x1 in runs]


def _tight_copy(surface):
    """Copia só a parte visível da superfície. Retorna None se estiver vazia."""
    bounds = surface.get_bounding_rect(min_alpha=ALPHA_MIN)
    if bounds.width == 0 or bounds.height == 0:
        return None
    return surface.subsurface(bounds).copy()


def _build_design(sheet, rects):
    """Monta os frames de um design com o mesmo tamanho.

    Retorna None se nenhum frame tiver nave visível.
    """
    tight = [_tight_copy(sheet.subsurface(rect)) for rect in rects]
    visible = [frame for frame in tight if frame is not None]
    if not visible:
        return None

    width = max(frame.get_width() for frame in visible)
    height = max(frame.get_height() for frame in visible)
    new_size = (round(width * SHIP_SCALE), round(height * SHIP_SCALE))

    result = []
    for frame in tight:
        canvas = pygame.Surface((width, height), pygame.SRCALPHA)
        if frame is not None:
            canvas.blit(frame, ((width - frame.get_width()) // 2, 0))
        # scale mantém os pixels nítidos, como em pixel art.
        result.append(pygame.transform.scale(canvas, new_size))
    return result