import pygame


class ImageButton:
    def __init__(
        self,
        image_path,
        center,
        on_click,
        scale=1.0,
        hover_scale=1.12,
        scale_x=1.0,
        scale_y=1.0,
        alt_image_path=None,
        click_sound=None
    ):
        # =========================
        # LOAD IMAGE
        # =========================
        self.image_raw = pygame.image.load(image_path).convert_alpha()
        self.alt_raw = (
            pygame.image.load(alt_image_path).convert_alpha()
            if alt_image_path else None
        )

        # =========================
        # CONFIG SIZE
        # =========================
        self.scale = scale
        self.hover_scale = hover_scale
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.click_sound = click_sound

        # =========================
        # SCALE IMAGE
        # =========================
        self.image = self._scale(self.image_raw, scale)
        self.image_hover = self._scale(self.image_raw, scale * hover_scale)

        self.alt_image = (
            self._scale(self.alt_raw, scale) if self.alt_raw else None
        )
        self.alt_hover = (
            self._scale(self.alt_raw, scale * hover_scale)
            if self.alt_raw else None
        )

        # =========================
        # STATE
        # =========================
        self.center = center
        self.rect = self.image.get_rect(center=center)
        self.on_click = on_click
        self.hover = False
        self.pressed = False
        self.use_alt = False

    # =========================
    # SCALE
    # =========================
    def _scale(self, img, scale):
        w = int(img.get_width() * scale * self.scale_x)
        h = int(img.get_height() * scale * self.scale_y)
        return pygame.transform.smoothscale(img, (w, h))

    # =========================
    # PIXEL-PERFECT HOVER
    # =========================
    def _pixel_hover(self, img, rect, mouse_pos):
        if not rect.collidepoint(mouse_pos):
            return False

        # tọa độ chuột tương đối trong ảnh
        x = mouse_pos[0] - rect.left
        y = mouse_pos[1] - rect.top

        try:
            # kiểm tra alpha (pixel trong suốt hay không)
            return img.get_at((int(x), int(y))).a > 10
        except IndexError:
            return False

    # =========================
    # EVENTS
    # =========================
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # chọn ảnh đang hiển thị để test hover
        if self.use_alt and self.alt_raw:
            img = self.alt_hover if self.hover else self.alt_image
        else:
            img = self.image_hover if self.hover else self.image

        if event.type == pygame.MOUSEMOTION:
            self.hover = self._pixel_hover(img, self.rect, mouse_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover:
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.hover:
                if self.click_sound:
                    self.click_sound.play()

                self.on_click()

                if self.alt_raw:
                    self.use_alt = not self.use_alt

            self.pressed = False

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        # chọn ảnh theo trạng thái
        if self.use_alt and self.alt_raw:
            img = self.alt_hover if self.hover else self.alt_image
        else:
            img = self.image_hover if self.hover else self.image

        # ⭐ rect LUÔN KHỚP ẢNH ĐANG VẼ
        self.rect = img.get_rect(center=self.center)
        screen.blit(img, self.rect)
