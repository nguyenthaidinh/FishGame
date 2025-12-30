import pygame
import math

class Button:
    def __init__(self, rect, text, on_click, font, theme):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.font = font
        self.theme = theme
        self.hover = False
        self.disabled = False

    def handle_event(self, event):
        if self.disabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, screen):
        r = self.rect.copy()

        # hover scale nhẹ
        if self.hover and not self.disabled:
            inflate = 6
            r.inflate_ip(inflate, inflate)

        # shadow
        shadow = r.move(0, 6)
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow, border_radius=18)

        # main
        base = self.theme["btn"]
        if self.disabled:
            base = self.theme["btn_disabled"]
        elif self.hover:
            base = self.theme["btn_hover"]

        pygame.draw.rect(screen, base, r, border_radius=18)
        pygame.draw.rect(screen, self.theme["stroke"], r, width=2, border_radius=18)

        # text
        color = self.theme["text"]
        if self.disabled:
            color = self.theme["muted"]
        txt = self.font.render(self.text, True, color)
        screen.blit(txt, txt.get_rect(center=r.center))
