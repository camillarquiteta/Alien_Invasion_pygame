import pygame
from pygame.sprite import Sprite
from pathlib import Path

IMAGES_DIR = Path(__file__).parent / 'images'
ALIEN_SIZE = (50, 40)


class Alien(Sprite):
    """A class to represent a single alien in the fleet."""
    # Guarda a imagem já carregada e redimensionada, compartilhada por todos os aliens.
    _image = None    

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image only once.
        if Alien._image is None:
            image = pygame.image.load(IMAGES_DIR / 'alien2.png').convert_alpha()
            Alien._image = pygame.transform.scale(image, ALIEN_SIZE)

        self.image = Alien._image
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position.
        self.x = float(self.rect.x)

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)
    
    def update(self):
        """Move the alien right or left."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x