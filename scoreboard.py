import pygame


class Scoreboard:
    """Painel superior com nível, vidas, recorde e pontuação, em uma só linha."""

    MARGIN = 12  # distância das bordas laterais da tela
    TOP = 12     # distância do topo da tela

    def __init__(self, ai_game):
        """Inicia as fontes, o fundo do painel e os valores iniciais."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        self.label_font = pygame.font.SysFont('segoeui', 14, bold=True)
        self.value_font = pygame.font.SysFont('segoeui', 26, bold=True)
        self.record_font = pygame.font.SysFont('segoeui', 32, bold=True)

        self.label_color = (150, 150, 170)
        self.value_color = (255, 255, 255)

        # Fundo translúcido atrás do painel
        self.panel = pygame.Surface((self.screen_rect.width, 90), pygame.SRCALPHA)
        self.panel.fill((0, 0, 0, 110))

        self.prep_level()
        self.prep_ships()
        self.prep_high_score()
        self.prep_score()

    def _build_block(self, label, value):
        """Cria um bloco com o nome do campo em cima e o valor embaixo."""
        label_img = self.label_font.render(label, True, self.label_color)
        value_img = self.value_font.render(value, True, self.value_color)

        width = max(label_img.get_width(), value_img.get_width())
        height = label_img.get_height() + value_img.get_height()
        block = pygame.Surface((width, height), pygame.SRCALPHA)
        block.blit(label_img, ((width - label_img.get_width()) // 2, 0))
        block.blit(value_img, ((width - value_img.get_width()) // 2,
                               label_img.get_height()))
        return block

    def _layout_row(self):
        """Posiciona os quatro blocos em uma linha, com o mesmo espaço entre eles."""
        # Só organiza quando todos os blocos já foram criados.
        pairs = [
            ("level_image", "level_rect"),
            ("lives_image", "lives_rect"),
            ("high_score_image", "high_score_rect"),
            ("score_image", "score_rect"),
        ]
        if not all(hasattr(self, image_name) for image_name, _ in pairs):
            return

        images = [getattr(self, image_name) for image_name, _ in pairs]
        available = self.screen_rect.width - 2 * self.MARGIN
        total_width = sum(image.get_width() for image in images)
        gap = (available - total_width) / (len(images) - 1)

        x = self.MARGIN
        for image_name, rect_name in pairs:
            image = getattr(self, image_name)
            rect = image.get_rect(topleft=(round(x), self.TOP))
            setattr(self, rect_name, rect)
            x += image.get_width() + gap

    def prep_score(self):
        """Atualiza a pontuação e reorganiza a linha."""
        rounded = round(self.stats.score, -1)
        self.score_image = self._build_block("PONTOS", f"{rounded:,}")
        self._layout_row()

    def prep_high_score(self):
        """Atualiza o recorde e reorganiza a linha."""
        rounded = round(self.stats.high_score, -1)
        self.high_score_image = self._build_block("RECORDE", f"{rounded:,}")
        self._layout_row()

    def prep_level(self):
        """Atualiza o nível e reorganiza a linha."""
        self.level_image = self._build_block("NÍVEL", str(self.stats.level))
        self._layout_row()

    def prep_ships(self):
        """Atualiza as vidas e reorganiza a linha."""
        self.lives_image = self._build_block("VIDAS", str(self.stats.ships_left))
        self._layout_row()

    def check_high_score(self):
        """Atualiza o recorde quando a pontuação atual for maior."""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def show_score(self):
        """Desenha o painel superior na tela."""
        self.screen.blit(self.panel, (0, 0))
        self.screen.blit(self.level_image, self.level_rect)
        self.screen.blit(self.lives_image, self.lives_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.score_image, self.score_rect)

    def show_start_record(self, y):
        """Mostra o recorde em destaque na tela inicial, na altura y."""
        rounded = round(self.stats.high_score, -1)
        image = self.record_font.render(f"RECORDE  {rounded:,}", True, self.value_color)
        rect = image.get_rect(center=(self.screen_rect.centerx, y))
        self.screen.blit(image, rect)
