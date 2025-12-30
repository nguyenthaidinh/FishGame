import pygame
from src.core.scene import Scene
from src.ui.button import Button

class Settings:
    TITLE = "BIG FISH"
    WIDTH = 1280
    HEIGHT = 720
    FPS = 60
# =========================
# Helpers
# =========================
def draw_cover(screen, image, w, h, alpha=255):
    if image is None:
        return
    iw, ih = image.get_width(), image.get_height()
    if iw <= 0 or ih <= 0:
        return
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    surf = pygame.transform.smoothscale(image, (nw, nh))
    if alpha < 255:
        surf.set_alpha(alpha)
    x = (w - nw) // 2
    y = (h - nh) // 2
    screen.blit(surf, (x, y))


def clamp01(v):
    return 0.0 if v < 0 else 1.0 if v > 1 else v


# =========================
# UI Widgets
# =========================
class Slider:
    def __init__(self, rect, value=0.5):
        self.rect = pygame.Rect(rect)
        self.value = float(value)
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._set_by_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_by_mouse(event.pos[0])

    def _set_by_mouse(self, mx):
        x0 = self.rect.x + 14
        x1 = self.rect.right - 14
        if x1 <= x0:
            return
        self.value = clamp01((mx - x0) / (x1 - x0))

    def draw(self, screen, theme):
        pygame.draw.rect(screen, (18, 32, 52), self.rect, border_radius=14)
        pygame.draw.rect(screen, theme["stroke"], self.rect, 2, border_radius=14)

        fill_w = int((self.rect.w - 28) * self.value)
        fill_rect = pygame.Rect(
            self.rect.x + 14,
            self.rect.y + 10,
            fill_w,
            self.rect.h - 20
        )
        pygame.draw.rect(screen, theme["btn_hover"], fill_rect, border_radius=10)

        knob_x = self.rect.x + 14 + fill_w
        pygame.draw.circle(screen, (255, 235, 170), (knob_x, self.rect.centery), 10)
        pygame.draw.circle(screen, (0, 0, 0), (knob_x, self.rect.centery), 10, 2)


class Toggle:
    def __init__(self, rect, value=False):
        self.rect = pygame.Rect(rect)
        self.value = bool(value)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.value = not self.value

    def draw(self, screen, theme):
        pygame.draw.rect(screen, (18, 32, 52), self.rect, border_radius=18)
        pygame.draw.rect(screen, theme["stroke"], self.rect, 2, border_radius=18)

        pad = 6
        knob = pygame.Rect(
            self.rect.x + pad,
            self.rect.y + pad,
            (self.rect.w // 2) - pad,
            self.rect.h - pad * 2
        )
        if self.value:
            knob.x = self.rect.centerx
        pygame.draw.rect(
            screen,
            theme["btn_hover"] if self.value else (35, 45, 60),
            knob,
            border_radius=14
        )


# =========================
# SETTINGS SCENE
# =========================
class SettingsScene(Scene):
    def on_enter(self, **kwargs):
        self.bg = self.app.assets.image("assets/bg/khungchoi_bg.jpg")

        self.h1 = self.app.assets.font(None, 54)
        self.font = self.app.assets.font(None, 24)
        self.small = self.app.assets.font(None, 18)
        self.btn_font = self.app.assets.font(None, 26)

        # load settings
        s = self.app.save.data.setdefault("settings", {})
        self.music = float(s.get("music", 0.6))
        self.sfx = float(s.get("sfx", 0.7))
        self.fullscreen = bool(s.get("fullscreen", False))

        self.slider_music = Slider((360, 260, 520, 42), self.music)
        self.slider_sfx = Slider((360, 340, 520, 42), self.sfx)
        self.toggle_fs = Toggle((360, 420, 140, 44), self.fullscreen)

        theme = self.app.theme
        self.btn_back = Button((30, 20, 140, 44), "BACK", self._go_menu, self.small, theme)
        self.btn_apply = Button(
            (self.app.w // 2 - 160, 560, 320, 56),
            "APPLY",
            self._apply,
            self.btn_font,
            theme
        )

        self.toast = ""
        self.toast_t = 0.0

    # =========================
    # Navigation (FIX CIRCULAR IMPORT)
    # =========================
    def _go_menu(self):
        from src.scenes.menu import MenuScene
        self.app.scenes.set_scene(MenuScene(self.app))

    # =========================
    # Apply settings
    # =========================
    def _apply(self):
        self.music = float(self.slider_music.value)
        self.sfx = float(self.slider_sfx.value)
        self.fullscreen = bool(self.toggle_fs.value)

        self.app.save.data.setdefault("settings", {})
        self.app.save.data["settings"].update({
            "music": self.music,
            "sfx": self.sfx,
            "fullscreen": self.fullscreen
        })
        self.app.save.save()

        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.app.screen = pygame.display.set_mode((self.app.w, self.app.h), flags)

        try:
            pygame.mixer.music.set_volume(self.music)
        except Exception:
            pass

        self.toast = "Applied!"
        self.toast_t = 1.4

    # =========================
    # Events
    # =========================
    def handle_event(self, event):
        self.btn_back.handle_event(event)
        self.btn_apply.handle_event(event)

        self.slider_music.handle_event(event)
        self.slider_sfx.handle_event(event)
        self.toggle_fs.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_menu()

    def update(self, dt):
        if self.toast_t > 0:
            self.toast_t -= dt
            if self.toast_t <= 0:
                self.toast = ""

    # =========================
    # Draw
    # =========================
    def draw(self, screen):
        draw_cover(screen, self.bg, self.app.w, self.app.h)

        overlay = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 105))
        screen.blit(overlay, (0, 0))

        title = self.h1.render("SETTINGS", True, self.app.theme["text"])
        screen.blit(title, (70, 70))

        panel = pygame.Rect(70, 160, self.app.w - 140, 520)
        pygame.draw.rect(screen, (10, 20, 35), panel, border_radius=18)
        pygame.draw.rect(screen, (120, 200, 255), panel, 2, border_radius=18)

        screen.blit(self.font.render("Music Volume", True, (235, 245, 255)), (160, 266))
        screen.blit(self.font.render("SFX Volume", True, (235, 245, 255)), (160, 346))
        screen.blit(self.font.render("Fullscreen", True, (235, 245, 255)), (160, 426))

        self.slider_music.draw(screen, self.app.theme)
        self.slider_sfx.draw(screen, self.app.theme)
        self.toggle_fs.draw(screen, self.app.theme)

        screen.blit(self.small.render(f"{int(self.slider_music.value*100)}%", True, self.app.theme["muted"]), (900, 270))
        screen.blit(self.small.render(f"{int(self.slider_sfx.value*100)}%", True, self.app.theme["muted"]), (900, 350))
        screen.blit(self.small.render("ON" if self.toggle_fs.value else "OFF", True, self.app.theme["muted"]), (520, 430))

        self.btn_back.draw(screen)
        self.btn_apply.draw(screen)

        if self.toast:
            t = self.small.render(self.toast, True, (255, 235, 170))
            screen.blit(t, t.get_rect(center=(self.app.w // 2, 640)))
