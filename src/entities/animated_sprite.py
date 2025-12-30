import pygame

class AnimatedSprite:
    def __init__(self, image_paths, fps=8):
        self.frames = [pygame.image.load(p).convert_alpha() for p in image_paths]
        self.fps = fps
        self.index = 0
        self.timer = 0.0
        self.flip_x = False

        self.base_w = self.frames[0].get_width()
        self.base_h = self.frames[0].get_height()
        self._cache = {}  # (idx,w,h,flip) -> surface

    def update(self, dt):
        self.timer += dt
        if self.timer >= 1 / self.fps:
            self.timer = 0.0
            self.index = (self.index + 1) % len(self.frames)

    def get_image(self, scale=1.0):
        scale = max(0.25, min(5.0, float(scale)))
        w = max(1, int(self.base_w * scale))
        h = max(1, int(self.base_h * scale))
        key = (self.index, w, h, self.flip_x)

        if key in self._cache:
            return self._cache[key]

        img = self.frames[self.index]
        if (img.get_width(), img.get_height()) != (w, h):
            img = pygame.transform.smoothscale(img, (w, h))
        if self.flip_x:
            img = pygame.transform.flip(img, True, False)

        self._cache[key] = img
        return img
