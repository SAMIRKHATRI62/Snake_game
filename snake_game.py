"""Simple Snake game using pygame.

Controls:
- Arrow keys / WASD: move
- R: restart after game over
- Esc: quit

Requires: pygame (pip install -r requirements.txt)
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass


try:
    import pygame
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "pygame is not installed.\n"
        "Install it with: pip install -r requirements.txt\n"
    ) from exc


Vec = tuple[int, int]


@dataclass(frozen=True)
class Config:
    cell_size: int = 20
    grid_width: int = 30
    grid_height: int = 20

    bg_color: tuple[int, int, int] = (18, 18, 18)
    snake_color: tuple[int, int, int] = (80, 220, 120)
    head_color: tuple[int, int, int] = (50, 190, 95)
    food_color: tuple[int, int, int] = (220, 80, 80)
    text_color: tuple[int, int, int] = (235, 235, 235)

    base_fps: int = 5
    speedup_every: int = 5
    speedup_amount: int = 2

    @property
    def width_px(self) -> int:
        return self.grid_width * self.cell_size

    @property
    def height_px(self) -> int:
        return self.grid_height * self.cell_size


def add(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1])


def inside(pos: Vec, cfg: Config) -> bool:
    return 0 <= pos[0] < cfg.grid_width and 0 <= pos[1] < cfg.grid_height


def random_empty_cell(occupied: set[Vec], cfg: Config) -> Vec:
    empties = [
        (x, y)
        for y in range(cfg.grid_height)
        for x in range(cfg.grid_width)
        if (x, y) not in occupied
    ]
    if not empties:
        # Snake fills the board; treat as win.
        return (-1, -1)
    return random.choice(empties)


def draw_cell(surface: pygame.Surface, pos: Vec, color: tuple[int, int, int], cfg: Config) -> None:
    rect = pygame.Rect(
        pos[0] * cfg.cell_size,
        pos[1] * cfg.cell_size,
        cfg.cell_size,
        cfg.cell_size,
    )
    pygame.draw.rect(surface, color, rect)


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    x: int,
    y: int,
) -> None:
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def run() -> None:
    cfg = Config()

    pygame.init()
    pygame.display.set_caption("Snake")
    screen = pygame.display.set_mode((cfg.width_px, cfg.height_px))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 44)

    def reset_game() -> tuple[list[Vec], Vec, Vec, bool, int]:
        start = (cfg.grid_width // 2, cfg.grid_height // 2)
        snake = [start, (start[0] - 1, start[1]), (start[0] - 2, start[1])]
        direction = (1, 0)
        pending_dir = direction
        food = random_empty_cell(set(snake), cfg)
        alive = True
        score = 0
        return snake, direction, pending_dir, alive, score, food

    snake, direction, pending_dir, alive, score, food = reset_game()

    def current_fps(score_value: int) -> int:
        return cfg.base_fps + (score_value // cfg.speedup_every) * cfg.speedup_amount

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

                if not alive and event.key == pygame.K_r:
                    snake, direction, pending_dir, alive, score, food = reset_game()
                    continue

                if alive:
                    # Direction input (prevent direct reversal)
                    if event.key in (pygame.K_UP, pygame.K_w):
                        if direction != (0, 1):
                            pending_dir = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if direction != (0, -1):
                            pending_dir = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if direction != (1, 0):
                            pending_dir = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if direction != (-1, 0):
                            pending_dir = (1, 0)

        screen.fill(cfg.bg_color)

        if alive:
            direction = pending_dir
            new_head = add(snake[0], direction)

            if not inside(new_head, cfg) or new_head in snake:
                alive = False
            else:
                snake.insert(0, new_head)

                if new_head == food:
                    score += 1
                    food = random_empty_cell(set(snake), cfg)
                else:
                    snake.pop()  # move forward

        # Draw food
        if food != (-1, -1):
            draw_cell(screen, food, cfg.food_color, cfg)

        # Draw snake
        if snake:
            draw_cell(screen, snake[0], cfg.head_color, cfg)
            for seg in snake[1:]:
                draw_cell(screen, seg, cfg.snake_color, cfg)

        # HUD
        draw_text(screen, f"Score: {score}", font, cfg.text_color, 8, 6)
        draw_text(screen, f"Speed: {current_fps(score)}", font, cfg.text_color, 8, 28)

        if not alive:
            # Game over overlay text
            msg1 = "Game Over"
            msg2 = "Press R to restart, Esc to quit"
            img1 = big_font.render(msg1, True, cfg.text_color)
            img2 = font.render(msg2, True, cfg.text_color)
            x1 = (cfg.width_px - img1.get_width()) // 2
            y1 = (cfg.height_px - img1.get_height()) // 2 - 18
            x2 = (cfg.width_px - img2.get_width()) // 2
            y2 = y1 + img1.get_height() + 10
            screen.blit(img1, (x1, y1))
            screen.blit(img2, (x2, y2))

        pygame.display.flip()
        clock.tick(current_fps(score))


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
