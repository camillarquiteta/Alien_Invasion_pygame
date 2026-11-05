class Settings:
    """Armazena todas as configurações do Alien Invasion."""

    def __init__(self):
        """Inicia as configurações fixas e depois as dinâmicas."""
        # Tela em formato de celular
        self.screen_width = 400
        self.screen_height = 800
        self.bg_color = (30, 30, 35)

        self.ship_limit = 3

        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 220, 80)
        self.bullets_allowed = 300
        self.bullet_cooldown = 250

        # Tiros dos aliens
        self.enemy_bullet_color = (230, 60, 60)
        self.enemy_bullet_width = 3
        self.enemy_bullet_height = 10  # antes era 15 (o tamanho da bala da nave)
        self.enemy_burst_gap = 150  # ms entre tiros de uma mesma rajada

        self.speedup_scale = 1.1
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Valores iniciais das configurações que mudam durante o jogo."""
        self.ship_speed = 1.5
        self.bullet_speed = 2.5

        # Velocidade lateral dos aliens na formação
        self.alien_speed = 0.8
        # fleet_direction: 1 é direita, -1 é esquerda.
        self.fleet_direction = 1

        self.alien_points = 50

        # Tiros dos aliens (começa fácil)
        self.enemy_bullet_speed = 1.5
        self.enemy_fire_delay = 4000  # ms médios entre rajadas
        self.enemy_shots_max = 2      # tiros por rajada: sorteia de 1 até este valor

        # Descida dos aliens
        self.dive_speed = 1.0
        self.dive_interval = 3000  # ms entre descidas
        self.dive_turn = 0.03

        # Quantas ondas foram vencidas nesta partida
        self.waves_cleared = 0

    def increase_speed(self):
        """Aumenta a dificuldade ao passar de nível."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)

        self.enemy_bullet_speed *= self.speedup_scale
        self.enemy_fire_delay = max(1000, int(self.enemy_fire_delay / self.speedup_scale))

        self.dive_speed *= self.speedup_scale
        self.dive_interval = max(500, int(self.dive_interval / self.speedup_scale))

        # A cada 2 ondas vencidas, os aliens podem atirar uma rajada maior (máximo 4).
        self.waves_cleared += 1
        if self.waves_cleared % 2 == 0:
            self.enemy_shots_max = min(4, self.enemy_shots_max + 1)