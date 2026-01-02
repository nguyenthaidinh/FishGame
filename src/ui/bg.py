import pygame

def draw_cover(screen, image, w, h, alpha=255):
    """Draw image cover the screen while keeping aspect ratio."""
    if image is None:
        return
    iw, ih = image.get_width(), image.get_height()
    if iw == 0 or ih == 0:
        return

    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    surf = pygame.transform.smoothscale(image, (nw, nh))

    if alpha < 255:
        surf.set_alpha(alpha)

    x = (w - nw) // 2
    y = (h - nh) // 2
    screen.blit(surf, (x, y))
