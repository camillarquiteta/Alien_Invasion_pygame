import pygame
from pygame.sprite import Sprite
from sprites import load_ship_families
class Ship(Sprite):
    '''Classe que gerencia nossa nave'''
    def __init__(self,ai_game):
        '''Inicia a nave e pega a área retangular que envolve o objeto'''
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        '''Carrega a imagem e posiciona seu retangulo no jogo permitindo 
        que você controle a posição dela na tela e detecte colisões'''
        # Usa o primeiro design da sheet, no primeiro frame.
        self.image = load_ship_families()[0][0]
        self.rect = self.image.get_rect()

        '''Faz a nave começar do centro inferior da tela'''
        self.rect.midbottom = self.screen_rect.midbottom

        '''Guarda a posição horizontal exata como float.'''
        self.x = float(self.rect.x)

        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Update the ship's position based on the movement flag."""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed   
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
              
        # Update rect object from self.x.    
        self.rect.x = self.x


    def blitme(self):
        '''Atualiza a imagem no seu local correto'''
        self.screen.blit(self.image,self.rect)

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)




