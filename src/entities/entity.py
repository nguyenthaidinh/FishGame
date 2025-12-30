import pygame

class Entity:
    """Base entity class for OOP clean architecture."""
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.alive = True

    def update(self, dt, world_w, world_h, **kwargs):
        pass

    def draw(self, screen, camera, assets, **kwargs):
        pass

    def rect(self):
        """Override in subclasses for collision."""
        return pygame.Rect(int(self.pos.x), int(self.pos.y), 1, 1)
