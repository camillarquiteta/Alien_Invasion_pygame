class Settings:
    """Armazena configurações do Alien Invasion."""

    def __init__(self):
        """Inicia as configurações fixas e depois as dinâmicas."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Ship settings
        self.ship_limit = 3

        # Bullet settings
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 300
        self.bullet_cooldown = 250

        # Alien settings
        self.fleet_drop_speed = 10

        self.fleet_direction = 1

        # Game Speed per nivel
        self.speedup_scale = 1.1

        self.initialize_dynamic_settings()
        
        # How quickly the alien point values increase
        self.score_scale = 1.5

        #Game Dynamic Settings 
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 5
        self.bullet_speed = 3
        self.alien_speed = 1.0

        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        # score settings
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
