# src/ui/panel.py
import pygame


class Panel:
    def __init__(self, rect, bg_color=(30, 30, 40), alpha=200, radius=16):
        self.rect = pygame.Rect(rect)
        self.bg_color = bg_color
        self.alpha = alpha
        self.radius = radius

        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.children = []

    def add(self, widget):
        self.children.append(widget)

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))

        panel_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        panel_surf.fill((*self.bg_color, self.alpha))

        pygame.draw.rect(
            panel_surf,
            (*self.bg_color, self.alpha),
            panel_surf.get_rect(),
            border_radius=self.radius
        )

        self.surface.blit(panel_surf, (0, 0))
        screen.blit(self.surface, self.rect.topleft)

        for w in self.children:
            w.draw(screen)
