import pygame
from pygame.sprite import Sprite


class EnemyBullet(Sprite):
    """Tiro disparado pelos aliens. Desce sempre em linha reta."""

    def __init__(self, ai_game, origin, target=None):
        """Cria o tiro na posição origin. O parâmetro target é ignorado, porque os tiros não miram."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        self.rect = pygame.Rect(0, 0,
                                self.settings.enemy_bullet_width,
                                self.settings.enemy_bullet_height)
        self.rect.midtop = origin
        self.y = float(self.rect.y)

    def update(self):
        """Move o tiro para baixo."""
        self.y += self.settings.enemy_bullet_speed
        self.rect.y = round(self.y)

    def draw_bullet(self):
        """Desenha o tiro na tela."""
        pygame.draw.rect(self.screen, self.settings.enemy_bullet_color, self.rect)