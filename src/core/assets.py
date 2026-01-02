import os
import pygame
from typing import Optional


class Assets:
    def __init__(self):
        self._images = {}
        self._fonts = {}
        self._sounds = {}

    # ---------- IMAGE ----------
    def image(self, path: str):
        path = path.replace("\\", "/")

        if path not in self._images:
            if not os.path.exists(path):
                # fallback placeholder (màu tím debug)
                surf = pygame.Surface((256, 144), pygame.SRCALPHA)
                surf.fill((255, 0, 255, 160))
                self._images[path] = surf
            else:
                self._images[path] = pygame.image.load(path).convert_alpha()

        return self._images[path]

    # ---------- FONT ----------
    def font(self, path: Optional[str], size: int):
        key = (path, size)

        if key not in self._fonts:
            if path and os.path.exists(path):
                self._fonts[key] = pygame.font.Font(path, size)
            else:
                # fallback font hệ thống (dễ đọc)
                self._fonts[key] = pygame.font.SysFont("segoeui", size)

        return self._fonts[key]

    # ---------- SOUND ----------
    def sound(self, path: str):
        path = path.replace("\\", "/")

        if path not in self._sounds:
            if not os.path.exists(path):
                # sound rỗng (không crash)
                self._sounds[path] = None
            else:
                self._sounds[path] = pygame.mixer.Sound(path)

        return self._sounds[path]
