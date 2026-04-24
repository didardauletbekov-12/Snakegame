import pygame, json
from game import SnakeGame
from db import init_db, save_game, get_best, get_top

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 40)
small = pygame.font.SysFont(None, 25)

# settings
with open("settings.json") as f:
    settings = json.load(f)

init_db()

state = "menu"
username = ""
game = None
best = 0

running = True

while running:
    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username:
                    best = get_best(username)
                    game = SnakeGame()
                    state = "game"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_l:
                    state = "leaderboard"
                elif event.key == pygame.K_s:
                    state = "settings"
                else:
                    username += event.unicode

        elif state == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.direction = (0,-20)
                elif event.key == pygame.K_DOWN:
                    game.direction = (0,20)
                elif event.key == pygame.K_LEFT:
                    game.direction = (-20,0)
                elif event.key == pygame.K_RIGHT:
                    game.direction = (20,0)

        elif state == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    state = "menu"
                    username = ""

        elif state == "leaderboard":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "menu"

        elif state == "settings":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    settings["grid"] = not settings["grid"]
                elif event.key == pygame.K_q:
                    with open("settings.json","w") as f:
                        json.dump(settings,f,indent=4)
                    state = "menu"

    if state == "menu":
        screen.blit(font.render("Enter Username:",True,(255,255,255)),(150,120))
        screen.blit(font.render(username,True,(0,255,0)),(180,170))

        screen.blit(small.render("ENTER start",True,(200,200,200)),(200,210))
        screen.blit(small.render("L leaderboard",True,(200,200,200)),(200,240))
        screen.blit(small.render("S settings",True,(200,200,200)),(200,270))

    elif state == "game":
        alive = game.update()

        if not alive:
            save_game(username, game.score, game.level)
            state = "game_over"

        # snake
        for s in game.snake:
            pygame.draw.rect(screen, tuple(settings["snake_color"]), (*s,20,20))

        # food
        pygame.draw.rect(screen,(255,0,0),(*game.food,20,20))

        # poison
        pygame.draw.rect(screen,(150,0,0),(*game.poison,20,20))

        # obstacles
        for o in game.obstacles:
            pygame.draw.rect(screen,(100,100,100),(*o,20,20))

        # power
        if game.power:
            color = (0,0,255)
            if game.power[1]=="speed": color=(0,255,255)
            if game.power[1]=="slow": color=(255,255,0)
            if game.power[1]=="shield": color=(255,0,255)
            pygame.draw.rect(screen,color,(*game.power[0],20,20))

        # grid
        if settings["grid"]:
            for x in range(0,WIDTH,20):
                pygame.draw.line(screen,(50,50,50),(x,0),(x,HEIGHT))
            for y in range(0,HEIGHT,20):
                pygame.draw.line(screen,(50,50,50),(0,y),(WIDTH,y))

        screen.blit(small.render(f"Score:{game.score}",True,(255,255,255)),(10,10))
        screen.blit(small.render(f"Level:{game.level}",True,(255,255,255)),(10,30))
        screen.blit(small.render(f"Best:{best}",True,(255,255,255)),(10,50))

    elif state == "game_over":
        screen.blit(font.render("GAME OVER",True,(255,0,0)),(180,150))
        screen.blit(small.render("ENTER menu",True,(200,200,200)),(200,200))

    elif state == "leaderboard":
        screen.blit(font.render("TOP 10",True,(255,255,0)),(200,40))
        data = get_top()
        y=100
        for i,row in enumerate(data):
            txt = small.render(f"{i+1}. {row[0]} {row[1]} L{row[2]}",True,(255,255,255))
            screen.blit(txt,(120,y))
            y+=25
        screen.blit(small.render("ESC back",True,(200,200,200)),(220,330))

    elif state == "settings":
        screen.blit(font.render("SETTINGS",True,(255,255,255)),(200,80))
        screen.blit(small.render(f"G grid: {settings['grid']}",True,(255,255,255)),(180,150))
        screen.blit(small.render("Q save & back",True,(200,200,200)),(180,200))

    pygame.display.flip()
    clock.tick(game.speed if game else 10)

pygame.quit()