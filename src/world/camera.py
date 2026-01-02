# src/world/camera.py
import pygame
import random


class Camera:
    """
    Camera 2D:
    - follow player
    - clamp trong world
    - world_to_screen trả về Vector2
    - shake ổn định (không dùng pygame.Vector2.random)
    - tương thích spawner: sw/sh
    """

    def __init__(self, screen_w, screen_h, world_w, world_h):
        self.screen_w = int(screen_w)
        self.screen_h = int(screen_h)

        # giữ sw/sh cho spawner
        self.sw = self.screen_w
        self.sh = self.screen_h

        self.world_w = int(world_w)
        self.world_h = int(world_h)

        self.offset = pygame.Vector2(0, 0)

        # shake
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self._shake_offset = pygame.Vector2(0, 0)

        self.zoom = 1.0

    def follow(self, target_pos: pygame.Vector2):
        self.offset.x = target_pos.x - self.screen_w / 2
        self.offset.y = target_pos.y - self.screen_h / 2

        # clamp an toàn (trường hợp world nhỏ hơn screen)
        max_x = max(0, self.world_w - self.screen_w)
        max_y = max(0, self.world_h - self.screen_h)

        self.offset.x = max(0, min(self.offset.x, max_x))
        self.offset.y = max(0, min(self.offset.y, max_y))

    def world_to_screen(self, world_pos: pygame.Vector2) -> pygame.Vector2:
        pos = pygame.Vector2(
            world_pos.x - self.offset.x,
            world_pos.y - self.offset.y
        )
        return pos + self._shake_offset

    def screen_to_world(self, screen_pos: pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(
            screen_pos.x + self.offset.x,
            screen_pos.y + self.offset.y
        ) - self._shake_offset

    def shake(self, strength=6, time=0.25):
        self.shake_strength = float(strength)
        self.shake_time = float(time)

    def update(self, dt: float):
        if self.shake_time > 0:
            self.shake_time -= dt
            # random offset mỗi frame khi đang shake
            s = self.shake_strength
            self._shake_offset.x = random.uniform(-s, s)
            self._shake_offset.y = random.uniform(-s, s)

            if self.shake_time <= 0:
                self.shake_time = 0.0
                self.shake_strength = 0.0
                self._shake_offset.update(0, 0)
        else:
            self._shake_offset.update(0, 0)
