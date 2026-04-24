import pygame
from game import SnakeGame
from db import init_db, save_game, get_best

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

init_db()

state = "menu"
username = ""
game = None
best = 0

running = True

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ===== MENU =====
        if state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username != "":
                    best = get_best(username)
                    game = SnakeGame()
                    state = "game"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

        # ===== GAME =====
        elif state == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.direction = (0, -20)
                elif event.key == pygame.K_DOWN:
                    game.direction = (0, 20)
                elif event.key == pygame.K_LEFT:
                    game.direction = (-20, 0)
                elif event.key == pygame.K_RIGHT:
                    game.direction = (20, 0)

    # ===== MENU DRAW =====
    if state == "menu":
        title = font.render("Enter Username:", True, (255,255,255))
        name = font.render(username, True, (0,255,0))
        hint = pygame.font.SysFont(None, 25).render("Press ENTER to start", True, (200,200,200))

        screen.blit(title, (180, 120))
        screen.blit(name, (180, 170))
        screen.blit(hint, (180, 210))

    # ===== GAME LOOP =====
    elif state == "game":
        alive = game.update()

        if not alive:
            save_game(username, game.score, game.level)
            state = "game_over"

        # draw snake
        for s in game.snake:
            pygame.draw.rect(screen, (0,255,0), (*s,20,20))

        # food
        pygame.draw.rect(screen, (255,0,0), (*game.food,20,20))

        # poison
        pygame.draw.rect(screen, (150,0,0), (*game.poison,20,20))

        # text
        screen.blit(pygame.font.SysFont(None, 25).render(f"Score: {game.score}", True,(255,255,255)), (10,10))
        screen.blit(pygame.font.SysFont(None, 25).render(f"Level: {game.level}", True,(255,255,255)), (10,30))
        screen.blit(pygame.font.SysFont(None, 25).render(f"Best: {best}", True,(255,255,255)), (10,50))

    # ===== GAME OVER =====
    elif state == "game_over":
        over = font.render("GAME OVER", True, (255,0,0))
        score_text = pygame.font.SysFont(None, 30).render(f"Score: {game.score}", True, (255,255,255))
        hint = pygame.font.SysFont(None, 25).render("Press ENTER for Menu", True, (200,200,200))

        screen.blit(over, (200, 140))
        screen.blit(score_text, (220, 180))
        screen.blit(hint, (170, 220))

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            state = "menu"
            username = ""

    pygame.display.flip()
    clock.tick(10)

pygame.quit()