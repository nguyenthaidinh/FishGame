import pygame
import random

class Camera:
    def __init__(self, screen_w, screen_h, world_w, world_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.sw = screen_w
        self.sh = screen_h

        self.world_w = world_w
        self.world_h = world_h

        self.offset = pygame.Vector2(0, 0)

        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.zoom = 1.0

    def follow(self, target_pos: pygame.Vector2):
        self.offset.x = target_pos.x - self.screen_w // 2
        self.offset.y = target_pos.y - self.screen_h // 2

        self.offset.x = max(0, min(self.offset.x, self.world_w - self.screen_w))
        self.offset.y = max(0, min(self.offset.y, self.world_h - self.screen_h))

    def world_to_screen(self, world_pos: pygame.Vector2) -> pygame.Vector2:
        pos = pygame.Vector2(world_pos.x - self.offset.x, world_pos.y - self.offset.y)

        if self.shake_time > 0:
            pos.x += random.uniform(-1, 1) * self.shake_strength
            pos.y += random.uniform(-1, 1) * self.shake_strength

        return pos

    def screen_to_world(self, screen_pos: pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(screen_pos.x + self.offset.x, screen_pos.y + self.offset.y)

    def shake(self, strength=6, time=0.25):
        self.shake_strength = strength
        self.shake_time = time

    def update(self, dt: float):
        if self.shake_time > 0:
            self.shake_time -= dt
            if self.shake_time <= 0:
                self.shake_time = 0
                self.shake_strength = 0
