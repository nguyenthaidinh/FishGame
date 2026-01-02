import pygame


class Button:
    def __init__(self, rect, text, on_click, font, theme):
        self.base_rect = pygame.Rect(rect)
        self.rect = self.base_rect.copy()

        self.text = text
        self.on_click = on_click
        self.font = font
        self.theme = theme

        self.hover = False
        self.pressed = False
        self.disabled = False

        self.hover_t = 0.0
        self.press_t = 0.0

    # =========================
    # EVENTS
    # =========================
    def handle_event(self, event):
        if self.disabled:
            return

        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self.press_t = 1.0

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.on_click()
            self.pressed = False

    # =========================
    # UPDATE
    # =========================
    def update(self, dt):
        target = 1.0 if self.hover and not self.disabled else 0.0
        self.hover_t += (target - self.hover_t) * min(1.0, dt * 10)
        self.press_t = max(0.0, self.press_t - dt * 7)

        self.rect = self.base_rect.copy()
        self.rect.move_ip(0, int(self.press_t * 6))

    # =========================
    # DRAW – REAL GAME BUTTON
    # =========================
    def draw(self, screen):
        r = self.rect
        radius = r.h // 2

        # ===== WATER SHADOW (KHÔNG ĐEN) =====
        shadow = r.move(0, 8)
        pygame.draw.rect(
            screen,
            (0, 40, 80, 140),
            shadow,
            border_radius=radius
        )

        # ===== BASE BODY (TỐI) =====
        pygame.draw.rect(
            screen,
            (30, 90, 140),
            r,
            border_radius=radius
        )

        # ===== TOP BEVEL (SÁNG) =====
        top = pygame.Rect(r.x, r.y, r.w, r.h * 0.55)
        pygame.draw.rect(
            screen,
            (90, 170, 220),
            top,
            border_radius=radius
        )

        # ===== INNER HIGHLIGHT =====
        inner = r.inflate(-10, -10)
        pygame.draw.rect(
            screen,
            (140, 210, 245, 120),
            inner,
            2,
            border_radius=radius - 6
        )

        # ===== TEXT SHADOW =====
        txt = self.font.render(self.text, True, (0, 40, 70))
        screen.blit(txt, txt.get_rect(center=(r.centerx, r.centery + 2)))

        # ===== TEXT =====
        txt = self.font.render(self.text, True, (235, 245, 255))
        screen.blit(txt, txt.get_rect(center=r.center))
