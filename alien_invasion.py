import sys
import random
from pathlib import Path

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from enemy_bullet import EnemyBullet
from alien import Alien
from sprites import load_ship_families
from starfield import Starfield
from explosion import Explosion

SOUNDS_DIR = Path(__file__).parent / 'sounds'

# Altura da primeira fileira de aliens, abaixo do painel.
FIRST_ROW_Y = 100


class AlienInvasion:
    """Classe geral que gerencia os recursos e o comportamento do jogo."""

    def __init__(self):
        """Inicia o jogo e cria os recursos."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        self.shot_sound = pygame.mixer.Sound(SOUNDS_DIR / 'laser.ogg')
        self.shot_sound.set_volume(0.4)
        self.explosion_sound = pygame.mixer.Sound(SOUNDS_DIR / 'tir.mp3')
        self.explosion_sound.set_volume(0.6)

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.starfield = Starfield(self)
        self.explosions = Explosion(self.settings.bg_color)

        self.ship = Ship(self)
        self.ship_hidden = False  # True enquanto a nave explode
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self.game_active = False
        # Tiro contínuo ao segurar a barra de espaço.
        self.shooting = False
        self.last_shot_time = 0
        # Momento em que o próximo alien começa a descer.
        self.next_dive_time = 0

        self._create_wave()

        self.play_button = Button(self, "Play")

    def _draw_frame(self, overlay=None):
        """Desenha todos os elementos na tela, sem mostrar. Overlay é um texto opcional no centro."""
        self.screen.fill(self.settings.bg_color)
        self.starfield.draw()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for bullet in self.enemy_bullets.sprites():
            bullet.draw_bullet()
        if not self.ship_hidden:
            self.ship.blitme()
        self.aliens.draw(self.screen)
        self.explosions.draw(self.screen)
        self.sb.show_score()
        if not self.game_active:
            self.play_button.draw_button()
            self.sb.show_start_record(self.play_button.rect.top - 40)
        if overlay is not None:
            self.screen.blit(overlay, overlay.get_rect(center=self.screen.get_rect().center))

    def _update_screen(self):
        """Desenha a tela e mostra o resultado."""
        self._draw_frame()
        pygame.display.flip()

    def _pause_with_effects(self, duration, overlay=None):
        """Espera um tempo mantendo as explosões e as estrelas em movimento."""
        end = pygame.time.get_ticks() + duration
        while pygame.time.get_ticks() < end:
            pygame.event.pump()
            self.starfield.update()
            self.explosions.update()
            self._draw_frame(overlay)
            pygame.display.flip()
            self.clock.tick(60)

    def _check_events(self):
        """Responde a teclas e cliques do mouse."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Inicia um novo jogo quando o jogador clica em Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()

            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            self.bullets.empty()
            self.enemy_bullets.empty()
            self.aliens.empty()
            self._create_wave()
            self.ship.center_ship()
            self.next_dive_time = pygame.time.get_ticks() + self.settings.dive_interval

            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Responde ao pressionar de teclas."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE and self.game_active:
            self.shooting = True

    def _check_keyup_events(self, event):
        """Responde ao soltar de teclas."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_SPACE:
            self.shooting = False

    def _fire_bullet(self):
        """Cria um tiro da nave, toca o som e o adiciona ao grupo."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            self.shot_sound.play()

    def _handle_shooting(self):
        """Dispara enquanto a barra de espaço estiver pressionada."""
        if self.shooting:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time >= self.settings.bullet_cooldown:
                self._fire_bullet()
                self.last_shot_time = now

    def _update_bullets(self):
        """Move os tiros da nave e remove os que saíram da tela."""
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Responde às colisões entre tiros da nave e aliens."""
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                for alien in aliens:
                    self.explosions.add(alien.rect, alien.image)
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

    def _update_alien_fire(self):
        """Faz cada alien disparar quando for a vez dele."""
        now = pygame.time.get_ticks()
        for alien in self.aliens.sprites():
            if alien.ready_to_fire(now):
                self.enemy_bullets.add(
                    EnemyBullet(self, alien.rect.midbottom, self.ship.rect.center))

    def _update_enemy_bullets(self):
        """Move os tiros dos aliens e verifica se atingiram a nave."""
        self.enemy_bullets.update()

        screen_rect = self.screen.get_rect()
        for bullet in self.enemy_bullets.copy():
            if not screen_rect.colliderect(bullet.rect):
                self.enemy_bullets.remove(bullet)

        if pygame.sprite.spritecollideany(self.ship, self.enemy_bullets):
            self._ship_hit()

    def _update_dives(self):
        """Escolhe um alien da formação para começar a descer."""
        now = pygame.time.get_ticks()
        if now < self.next_dive_time:
            return
        self.next_dive_time = now + self.settings.dive_interval

        formation = [alien for alien in self.aliens.sprites() if not alien.diving]
        if formation:
            random.choice(formation).start_dive()

    def _update_aliens(self):
        """Atualiza a posição dos aliens e verifica colisões com a nave."""
        self._check_fleet_edges()
        self.aliens.update(self.ship.rect.centerx)
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._remove_aliens_below_screen()

    def _remove_aliens_below_screen(self):
        """Remove os aliens que passaram da nave e saíram da tela."""
        for alien in self.aliens.copy():
            if alien.rect.top >= self.settings.screen_height:
                self.aliens.remove(alien)

    def _check_wave_cleared(self):
        """Mostra o aviso de próximo nível e cria a nova onda."""
        if self.game_active and not self.aliens:
            self.stats.level += 1
            self.sb.prep_level()
            self._show_level_banner(f"NÍVEL {self.stats.level}")

            self.settings.increase_speed()
            self.bullets.empty()
            self.enemy_bullets.empty()
            self._create_wave()
            self.next_dive_time = pygame.time.get_ticks() + self.settings.dive_interval

    def _show_level_banner(self, text):
        """Mostra o aviso do nível por 1 segundo, com as explosões ainda em andamento."""
        font = pygame.font.SysFont('segoeui', 52, bold=True)
        image = font.render(text, True, (255, 255, 255))
        self._pause_with_effects(1000, overlay=image)

    def _create_wave(self):
        """Cria uma onda: uma fileira no nível 1 e, depois, uma ou duas fileiras."""
        frame_w, frame_h = load_ship_families()[0][0].get_size()
        rows = 1 if self.stats.level == 1 else random.choice((1, 2))

        # Posições possíveis na horizontal, com espaço entre um alien e outro.
        columns = list(range(frame_w, self.settings.screen_width - frame_w, 2 * frame_w))

        for row in range(rows):
            # Cada fileira tem uma quantidade diferente de aliens.
            count = random.randint(max(2, len(columns) - 2), len(columns))
            for x in sorted(random.sample(columns, count)):
                self._create_alien(x, FIRST_ROW_Y + row * 2 * frame_h)

    def _create_alien(self, x_position, y_position):
        """Cria um alien com design sorteado e o posiciona."""
        frames = random.choice(load_ship_families())
        new_alien = Alien(self, frames)
        new_alien.x = float(x_position)
        new_alien.y = float(y_position)
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Inverte a direção da formação se algum alien da fileira chegar à borda."""
        for alien in self.aliens.sprites():
            if not alien.diving and alien.check_edges():
                self.settings.fleet_direction *= -1
                break

    def _ship_hit(self):
        """Faz a nave explodir e, se ainda houver vidas, cria uma nova onda."""
        self.explosion_sound.play()

        # A explosão começa antes de qualquer outra coisa, usando a imagem atual da nave.
        self.explosions.add(self.ship.rect, self.ship.image,
                            speed_range=(2.0, 6.0), life_range=(35, 60))
        self.ship_hidden = True

        self.bullets.empty()
        self.enemy_bullets.empty()
        self.aliens.empty()

        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            self._pause_with_effects(800)
            self.ship_hidden = False

            self._create_wave()
            self.ship.center_ship()
            self.next_dive_time = pygame.time.get_ticks() + self.settings.dive_interval
        else:
            self._pause_with_effects(800)
            self.ship_hidden = False
            self.game_active = False
            pygame.mouse.set_visible(True)

    def run_game(self):
        """Inicia o loop principal do jogo."""
        while True:
            self._check_events()
            self.starfield.update()
            self.explosions.update()
            if self.game_active:
                self.ship.update()
                self._handle_shooting()
                self._update_bullets()
                self._update_alien_fire()
                self._update_enemy_bullets()
                self._update_dives()
                self._update_aliens()
                self._check_wave_cleared()
            self._update_screen()
            self.clock.tick(60)


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()