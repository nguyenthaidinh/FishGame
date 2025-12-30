import pygame

class FloatingText:
    def __init__(self, pos, text, color=(255, 240, 180), lifetime=0.9):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, -55)
        self.text = text
        self.color = color
        self.life = lifetime
        self.max_life = lifetime

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        return self.life > 0

    def draw(self, screen, camera, font):
        alpha = max(0, min(255, int(255 * (self.life / self.max_life))))
        surf = font.render(self.text, True, self.color).convert_alpha()
        surf.set_alpha(alpha)
        p = camera.world_to_screen(self.pos)
        screen.blit(surf, surf.get_rect(center=(int(p.x), int(p.y))))
