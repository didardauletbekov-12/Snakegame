import pygame, json
from game import SnakeGame
from db import init_db, save_game, get_best, get_top

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

font      = pygame.font.SysFont(None, 48)
med_font  = pygame.font.SysFont(None, 36)
small     = pygame.font.SysFont(None, 26)

# ── settings ──────────────────────────────────────────────────────────────────
with open("settings.json") as f:
    settings = json.load(f)

init_db()

# ── Button helper ──────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text,
                 color=(60, 60, 180), hover_color=(90, 90, 220), text_color=(255, 255, 255)):
        self.rect        = pygame.Rect(x, y, w, h)
        self.text        = text
        self.color       = color
        self.hover_color = hover_color
        self.text_color  = text_color

    def draw(self, surf):
        mouse = pygame.mouse.get_pos()
        col   = self.hover_color if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surf, col, self.rect, border_radius=8)
        pygame.draw.rect(surf, (200, 200, 200), self.rect, 2, border_radius=8)
        lbl = med_font.render(self.text, True, self.text_color)
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── Menu buttons ───────────────────────────────────────────────────────────────
BTN_W, BTN_H = 200, 44
cx = WIDTH // 2 - BTN_W // 2

btn_play        = Button(cx, 200, BTN_W, BTN_H, "▶  Play")
btn_leaderboard = Button(cx, 255, BTN_W, BTN_H, "🏆  Leaderboard",  (60,130,60),  (90,170,90))
btn_settings    = Button(cx, 310, BTN_W, BTN_H, "⚙  Settings",      (130,90,30),  (180,130,40))
btn_quit        = Button(cx, 355, BTN_W, BTN_H, "✕  Quit",          (160,40,40),  (210,60,60))

# Game-Over buttons
btn_retry = Button(cx, 230, BTN_W, BTN_H, "↺  Retry")
btn_menu  = Button(cx, 285, BTN_W, BTN_H, "⌂  Main Menu", (80,80,80), (120,120,120))

# Leaderboard / Settings back
btn_back = Button(cx, 340, BTN_W, BTN_H, "← Back", (80,80,80), (120,120,120))

# Settings toggles
btn_grid  = Button(cx, 160, BTN_W, BTN_H, "", (60,60,130), (90,90,180))
btn_sound = Button(cx, 215, BTN_W, BTN_H, "", (60,60,130), (90,90,180))
btn_save  = Button(cx, 300, BTN_W, BTN_H, "💾  Save & Back", (60,130,60), (90,170,90))

# ── State ─────────────────────────────────────────────────────────────────────
state    = "menu"
username = ""
game     = None
best     = 0

running  = True

while running:
    screen.fill((15, 15, 25))

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # ── MENU ──────────────────────────────────────────────────────────────
        if state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN and username.strip():
                    best = get_best(username)
                    game = SnakeGame()
                    state = "game"
                else:
                    if len(username) < 20:
                        username += event.unicode

            if btn_play.clicked(event):
                if username.strip():
                    best = get_best(username)
                    game = SnakeGame()
                    state = "game"

            if btn_leaderboard.clicked(event):
                state = "leaderboard"

            if btn_settings.clicked(event):
                state = "settings"

            if btn_quit.clicked(event):
                running = False

        # ── GAME ──────────────────────────────────────────────────────────────
        elif state == "game":
            if event.type == pygame.KEYDOWN:
                d = game.direction
                if event.key == pygame.K_UP    and d != (0, 20):  game.direction = (0, -20)
                if event.key == pygame.K_DOWN  and d != (0,-20):  game.direction = (0,  20)
                if event.key == pygame.K_LEFT  and d != (20, 0):  game.direction = (-20, 0)
                if event.key == pygame.K_RIGHT and d != (-20,0):  game.direction = (20,  0)

        # ── GAME OVER ─────────────────────────────────────────────────────────
        elif state == "game_over":
            if btn_retry.clicked(event):
                best = get_best(username)
                game = SnakeGame()
                state = "game"
            if btn_menu.clicked(event):
                state = "menu"
                username = ""
                game = None

        # ── LEADERBOARD ───────────────────────────────────────────────────────
        elif state == "leaderboard":
            if btn_back.clicked(event) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                state = "menu"

        # ── SETTINGS ──────────────────────────────────────────────────────────
        elif state == "settings":
            if btn_grid.clicked(event):
                settings["grid"] = not settings["grid"]
            if btn_sound.clicked(event):
                settings["sound"] = not settings["sound"]
            if btn_save.clicked(event):
                with open("settings.json", "w") as f:
                    json.dump(settings, f, indent=4)
                state = "menu"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "menu"

    # ── DRAW ══════════════════════════════════════════════════════════════════

    if state == "menu":
        # Title
        title = font.render("🐍  SNAKE", True, (50, 220, 50))
        screen.blit(title, title.get_rect(centerx=WIDTH//2, y=40))

        # Username box
        box = pygame.Rect(cx, 130, BTN_W, 44)
        pygame.draw.rect(screen, (40, 40, 60), box, border_radius=6)
        pygame.draw.rect(screen, (100, 100, 200), box, 2, border_radius=6)
        if username:
            u_surf = med_font.render(username, True, (0, 255, 100))
        else:
            u_surf = med_font.render("Enter name...", True, (100, 100, 100))
        screen.blit(u_surf, u_surf.get_rect(center=box.center))

        btn_play.draw(screen)
        btn_leaderboard.draw(screen)
        btn_settings.draw(screen)
        btn_quit.draw(screen)

    elif state == "game":
        alive = game.update()

        if not alive:
            save_game(username, game.score, game.level)
            state = "game_over"

        # grid
        if settings.get("grid"):
            for x in range(0, WIDTH, 20):
                pygame.draw.line(screen, (30, 30, 40), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, 20):
                pygame.draw.line(screen, (30, 30, 40), (0, y), (WIDTH, y))

        # obstacles
        for o in game.obstacles:
            pygame.draw.rect(screen, (100, 100, 100), (*o, 20, 20))

        # food (bright red)
        pygame.draw.rect(screen, (255, 60, 60), (*game.food, 20, 20))

        # poison (dark red)
        pygame.draw.rect(screen, (160, 0, 0), (*game.poison, 20, 20))
        p_lbl = small.render("☠", True, (255, 100, 100))
        screen.blit(p_lbl, (game.poison[0]+2, game.poison[1]+1))

        # power-up
        if game.power:
            pw_colors = {"speed": (0,255,255), "slow": (255,255,0), "shield": (255,0,255)}
        if game.power:
            pygame.draw.rect(screen, pw_colors[game.power[1]], (*game.power[0], 20, 20))

        # snake
        for i, s in enumerate(game.snake):
            col = tuple(settings["snake_color"]) if i > 0 else (0, 255, 100)
            pygame.draw.rect(screen, col, (*s, 20, 20))

        # HUD
        screen.blit(small.render(f"Score: {game.score}", True, (255,255,255)), (10, 10))
        screen.blit(small.render(f"Level: {game.level}", True, (255,255,255)), (10, 30))
        screen.blit(small.render(f"Best:  {best}",       True, (200,200,100)), (10, 50))
        if game.power_active:
            hud = small.render(f"[{game.power_active.upper()}]", True, (100, 255, 255))
            screen.blit(hud, (WIDTH - 100, 10))

    elif state == "game_over":
        over  = font.render("GAME OVER", True, (255, 60, 60))
        sc    = med_font.render(f"Score: {game.score}   Level: {game.level}", True, (255,255,255))
        pb    = med_font.render(f"Personal Best: {get_best(username)}", True, (200, 200, 100))
        screen.blit(over, over.get_rect(centerx=WIDTH//2, y=100))
        screen.blit(sc,   sc.get_rect(centerx=WIDTH//2,   y=160))
        screen.blit(pb,   pb.get_rect(centerx=WIDTH//2,   y=195))
        btn_retry.draw(screen)
        btn_menu.draw(screen)

    elif state == "leaderboard":
        title = font.render("TOP 10", True, (255, 220, 0))
        screen.blit(title, title.get_rect(centerx=WIDTH//2, y=20))
        data = get_top()
        y = 90
        for i, row in enumerate(data):
            color = (255,215,0) if i == 0 else (200,200,200)
            txt = small.render(f"{i+1:>2}. {row[0]:<15} {row[1]:>5}pts  Lvl {row[2]}", True, color)
            screen.blit(txt, (80, y))
            y += 24
        btn_back.draw(screen)

    elif state == "settings":
        title = font.render("SETTINGS", True, (255, 255, 255))
        screen.blit(title, title.get_rect(centerx=WIDTH//2, y=60))

        # Grid toggle button
        btn_grid.text = f"Grid: {'ON ✔' if settings['grid'] else 'OFF ✘'}"
        btn_grid.draw(screen)

        # Sound toggle button
        btn_sound.text = f"Sound: {'ON ✔' if settings['sound'] else 'OFF ✘'}"
        btn_sound.draw(screen)

        # Snake color preview
        color_rect = pygame.Rect(cx, 270, BTN_W, 24)
        pygame.draw.rect(screen, tuple(settings["snake_color"]), color_rect, border_radius=4)
        lbl = small.render("Snake color", True, (200, 200, 200))
        screen.blit(lbl, lbl.get_rect(centerx=WIDTH//2, y=248))

        btn_save.draw(screen)

    pygame.display.flip()
    clock.tick(game.speed if (game and state == "game") else 30)

pygame.quit()