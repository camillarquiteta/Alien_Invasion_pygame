import math
import random

import pygame

ALPHA_MIN = 100      # pixels mais transparentes que isso não viram partículas
PARTICLE_SIZE = 2    # tamanho de cada pixel que se espalha, em px


class Particle:
    """Um pixel que se afasta do centro, perde força e some aos poucos."""

    def __init__(self, x, y, color, speed_range, life_range):
        """Cria a partícula com direção e velocidade sorteadas."""
        self.x = float(x)
        self.y = float(y)
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.max_life = random.randint(*life_range)
        self.life = self.max_life

    def update(self):
        """Move a partícula e reduz o tempo de vida."""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05   # leve gravidade
        self.vx *= 0.98   # atrito
        self.life -= 1

    def draw(self, screen, bg_color):
        """Desenha o pixel, misturando a cor com o fundo conforme ele envelhece."""
        ratio = self.life / self.max_life
        color = tuple(int(bg + (c - bg) * ratio)
                      for c, bg in zip(self.color, bg_color))
        pygame.draw.rect(screen, color,
                         (int(self.x), int(self.y), PARTICLE_SIZE, PARTICLE_SIZE))


class Explosion:
    """Guarda as partículas ativas e cuida da animação de explosão."""

    def __init__(self, bg_color):
        """Inicia sem partículas. bg_color é a cor do fundo, usada no desaparecimento."""
        self.bg_color = bg_color
        self.particles = []

    def add(self, rect, surface, speed_range=(1.0, 4.0), life_range=(25, 45), step=2):
        """Cria partículas a partir dos pixels visíveis de uma imagem.

        step é o espaçamento entre os pixels amostrados: 2 significa um a cada dois.
        """
        width, height = surface.get_size()
        for px in range(0, width, step):
            for py in range(0, height, step):
                pixel = surface.get_at((px, py))
                if pixel.a < ALPHA_MIN:
                    continue
                color = (pixel.r, pixel.g, pixel.b)
                self.particles.append(
                    Particle(rect.x + px, rect.y + py, color, speed_range, life_range))

    def update(self):
        """Atualiza as partículas e remove as que terminaram."""
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, screen):
        """Desenha todas as partículas ativas."""
        for particle in self.particles:
            particle.draw(screen, self.bg_color)