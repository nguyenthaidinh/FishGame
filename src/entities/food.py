import pygame
import random

class Food:
    def __init__(self, pos, radius=8):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.alive = True

    def draw(self, screen, camera):
        p = camera.world_to_screen(self.pos)
        pygame.draw.circle(screen, (255, 230, 120), (int(p.x), int(p.y)), self.radius)
        pygame.draw.circle(screen, (0, 0, 0), (int(p.x), int(p.y)), self.radius, 2)

    def rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius*2, self.radius*2)

def spawn_food(world_w, world_h, n=35):
    foods = []
    for _ in range(n):
        x = random.randint(80, world_w - 80)
        y = random.randint(80, world_h - 80)
        foods.append(Food((x, y), radius=random.randint(6, 10)))
    return foods
