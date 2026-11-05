import random

import pygame
from pygame.sprite import Sprite




class Alien(Sprite):
    """Um alien da frota: anda de lado na formação e depois desce na direção da nave."""

    def __init__(self, ai_game, frames):
        """Inicia o alien com o design sorteado."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Animação
        self.frames = frames
        self.frame_index = 0
        self.frame_delay = 120  # ms entre frames
        self.last_frame_time = pygame.time.get_ticks()
        self.image = frames[0]
        self.rect = self.image.get_rect()

        # Posição exata como float
        self.x = 0.0
        self.y = 0.0

        # False: anda na formação. True: está descendo.
        self.diving = False

        # Tiros
        self.shots_per_volley = random.randint(1, self.settings.enemy_shots_max)
        self.shots_left = 0
        self.next_shot_time = 0
        now = pygame.time.get_ticks()
        self.next_volley_time = now + random.randint(0, self.settings.enemy_fire_delay)

    def start_dive(self):
        """Faz o alien começar a descer na direção da nave."""
        self.diving = True

    def _animate(self):
        """Avança o frame quando o tempo de espera passar."""
        now = pygame.time.get_ticks()
        if now - self.last_frame_time >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.last_frame_time = now

    def ready_to_fire(self, now):
        """Retorna True se este alien deve disparar um tiro agora."""
        if self.shots_left == 0:
            if now < self.next_volley_time:
                return False
            # Começa uma nova rajada.
            self.shots_left = self.shots_per_volley
            self.next_shot_time = now

        if now < self.next_shot_time:
            return False

        self.shots_left -= 1
        self.next_shot_time = now + self.settings.enemy_burst_gap

        if self.shots_left == 0:
            # Rajada terminou: espera um tempo sorteado até a próxima.
            delay = self.settings.enemy_fire_delay
            self.next_volley_time = now + random.randint(delay // 2, delay)
        return True

    def check_edges(self):
        """Retorna True se o alien estiver na borda da tela."""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self, target_x=None):
        """Anima e move o alien.

        Na formação, anda de um lado para o outro. Quando está descendo,
        vai para baixo e corrige a direção para acompanhar a nave.
        """
        self._animate()
        if self.diving:
            self.y += self.settings.dive_speed
            if target_x is not None:
                diff = target_x - self.rect.centerx
                turn = max(-2.0, min(2.0, diff * self.settings.dive_turn))
                self.x += turn
        else:
            self.x += self.settings.alien_speed * self.settings.fleet_direction

        self.rect.x = round(self.x)
        self.rect.y = round(self.y)