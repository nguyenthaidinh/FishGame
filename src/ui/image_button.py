import pygame


class ImageButton:
    def __init__(
        self,
        image_path,
        center,
        on_click,
        scale=1.0,
        hover_scale=1.12,
        alt_image_path=None
    ):
        self.image_raw = pygame.image.load(image_path).convert_alpha()
        self.alt_raw = (
            pygame.image.load(alt_image_path).convert_alpha()
            if alt_image_path else None
        )

        self.scale = scale
        self.hover_scale = hover_scale

        self.image = self._scale(self.image_raw, scale)
        self.image_hover = self._scale(self.image_raw, scale * hover_scale)

        self.alt_image = (
            self._scale(self.alt_raw, scale) if self.alt_raw else None
        )
        self.alt_hover = (
            self._scale(self.alt_raw, scale * hover_scale)
            if self.alt_raw else None
        )

        self.use_alt = False

        self.rect = self.image.get_rect(center=center)
        self.on_click = on_click
        self.hover = False
        self.pressed = False

    def _scale(self, img, scale):
        w = int(img.get_width() * scale)
        h = int(img.get_height() * scale)
        return pygame.transform.scale(img, (w, h))

    # =========================
    # EVENTS
    # =========================
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover:
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.hover:
                self.on_click()
                if self.alt_raw:
                    self.use_alt = not self.use_alt
            self.pressed = False

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        if self.use_alt and self.alt_raw:
            img = self.alt_hover if self.hover else self.alt_image
        else:
            img = self.image_hover if self.hover else self.image

        rect = img.get_rect(center=self.rect.center)
        screen.blit(img, rect)
