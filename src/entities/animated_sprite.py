import os
import pygame


class AnimatedSprite:
    """
    1) Không dùng os.getcwd() (dễ lỗi khi chạy exe / chạy từ thư mục khác)
       -> dùng PROJECT_ROOT tính theo vị trí file này.
    2) Cache scale không phình vô hạn
       -> quantize scale + giới hạn cache (simple LRU-like).
    """

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    def __init__(self, image_paths, fps=8, max_cache=600, scale_step=0.05):
        self.frames = []
        self.fps = max(1, int(fps))
        self.index = 0
        self.timer = 0.0
        self.flip_x = False

        self.max_cache = int(max_cache)
        self.scale_step = float(scale_step)

        # cache: key -> Surface
        self._cache = {}
        # order list để pop old cache (nhẹ, đủ dùng)
        self._cache_order = []

        for p in image_paths:
            p = self._resolve_path(p)
            img = pygame.image.load(p).convert_alpha()
            self.frames.append(img)

        if not self.frames:
            raise ValueError("AnimatedSprite: image_paths is empty or cannot load any frames.")

        self.base_w = self.frames[0].get_width()
        self.base_h = self.frames[0].get_height()

    # =========================
    # Path resolver
    # =========================
    def _resolve_path(self, p: str) -> str:
        # normalize slash
        p = p.replace("\\", "/")

        if os.path.isabs(p) and os.path.exists(p):
            return p

        # thử ghép theo PROJECT_ROOT (ổn định hơn cwd)
        candidate = os.path.join(self.PROJECT_ROOT, p).replace("\\", "/")
        if os.path.exists(candidate):
            return candidate

        # fallback: đôi khi chạy dev vẫn đúng cwd
        candidate2 = os.path.abspath(p).replace("\\", "/")
        if os.path.exists(candidate2):
            return candidate2

        raise FileNotFoundError(f"AnimatedSprite: cannot find frame path: {p}")

    # =========================
    # Update
    # =========================
    def update(self, dt: float):
        self.timer += dt
        frame_time = 1.0 / self.fps
        while self.timer >= frame_time:
            self.timer -= frame_time
            self.index = (self.index + 1) % len(self.frames)

    # =========================
    # Cache helpers
    # =========================
    def _quantize_scale(self, s: float) -> float:
        s = max(0.25, min(5.0, float(s)))
        step = self.scale_step if self.scale_step > 0 else 0.05
        # làm tròn theo step để tránh cache phình
        return round(s / step) * step

    def _cache_put(self, key, surf):
        if key in self._cache:
            return

        self._cache[key] = surf
        self._cache_order.append(key)

        # giới hạn cache: pop các key cũ nhất
        while len(self._cache_order) > self.max_cache:
            old = self._cache_order.pop(0)
            self._cache.pop(old, None)

    # =========================
    # Render frame
    # =========================
    def get_image(self, scale=1.0):
        scale = self._quantize_scale(scale)

        w = max(1, int(self.base_w * scale))
        h = max(1, int(self.base_h * scale))
        key = (self.index, w, h, self.flip_x)

        cached = self._cache.get(key)
        if cached is not None:
            return cached

        img = self.frames[self.index]

        # scale
        if (img.get_width(), img.get_height()) != (w, h):
            img = pygame.transform.smoothscale(img, (w, h))

        # flip
        if self.flip_x:
            img = pygame.transform.flip(img, True, False)

        self._cache_put(key, img)
        return img
