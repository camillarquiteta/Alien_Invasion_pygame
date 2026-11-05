import random

import pygame


class Starfield:
    """Pontos brancos que descem devagar, dando sensação de movimento no espaço."""

    def __init__(self, ai_game, count=60):
        """Cria as estrelas espalhadas pela tela."""
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = (255, 255, 255)
        self.stars = [self._new_star(random_y=True) for _ in range(count)]

    def _new_star(self, random_y=False):
        """Cria uma estrela com posição, velocidade e tamanho sorteados."""
        x = random.randint(0, self.settings.screen_width)
        y = random.randint(0, self.settings.screen_height) if random_y else -2
        speed = random.uniform(0.2, 1.2)
        return [x, y, speed]

    def update(self):
        """Move as estrelas. Quando saem da tela, voltam no topo."""
        for i, star in enumerate(self.stars):
            star[1] += star[2]
            if star[1] > self.settings.screen_height:
                self.stars[i] = self._new_star()

    def draw(self):
        """Desenha as estrelas. As mais rápidas aparecem um pouco maiores."""
        for x, y, speed in self.stars:
            size = 2 if speed > 0.9 else 1
            pygame.draw.rect(self.screen, self.color, (int(x), int(y), size, size))