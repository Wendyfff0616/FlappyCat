import pygame
from pygame import mixer
import random

#initialize pygame
pygame.init()

#initialize the background music
pygame.mixer.init()

#load the music file and set the volume of music
pygame.mixer.music.load("music/xianzhou.mp3")
pygame.mixer.music.play(-1) #-1 means keep playing the music
pygame.mixer.music.set_volume(0.3)
jump = mixer.Sound("music/jump.wav")
jump.set_volume(0.3)
good = mixer.Sound("music/good.wav")
good.set_volume(0.3)
bad = mixer.Sound("music/bad.wav")
bad.set_volume(1)

#set clock and fps
clock = pygame.time.Clock()
fps = 30

#set the size of screen
screen_width = 740
screen_height = 440
screen = pygame.display.set_mode((screen_width, screen_height))
#set caption
pygame.display.set_caption("Flappy Cat")

#define font
font_big = pygame.font.SysFont("Bauhaus 93", 60)
font_small = pygame.font.SysFont("Bauhaus 93", 30)

#define colours
brown = (115, 74, 18)
white = (255, 255, 255)

#define game variables(global)
base_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 200
pipe_frequency = 2800  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
last_flower = pygame.time.get_ticks() - pipe_frequency
last_bad_flower = pygame.time.get_ticks() - pipe_frequency
score = 0
number_of_flowers = 0
pass_pipe = False
revive_chance = 0
invincible = False
invincible_start_time = 0
invincible_duration = 2000  # 2 seconds in milliseconds

#load icon
icon = pygame.image.load("images/icon.png")
pygame.display.set_icon(icon)
#load images
bg = pygame.image.load("images/bg.png")
base_img = pygame.image.load("images/base.jpg")
revive_img = pygame.image.load("images/revive.png")
restart_img = pygame.image.load("images/restart.png")
flower_img = pygame.image.load("images/flower.png")
bad_flower_img = pygame.image.load("images/bad_flower.png")


def draw_text_white(text, font, text_col, x, y, outline_col=(255, 255, 255)):
    img = font.render(text, True, outline_col)
    #draw outline by drawing the text offset by 2 pixel in each direction
    screen.blit(img, (x - 2, y - 2))
    screen.blit(img, (x + 2, y - 2))
    screen.blit(img, (x - 2, y + 2))
    screen.blit(img, (x + 2, y + 2))

    #draw the main text on top
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_text_blue(text, font, text_col, x, y, outline_col=(100, 149, 237)):
    img = font.render(text, True, outline_col)
    #draw outline by drawing the text offset by 1 pixel in each direction
    screen.blit(img, (x - 1, y - 1))
    screen.blit(img, (x + 1, y - 1))
    screen.blit(img, (x - 1, y + 1))
    screen.blit(img, (x + 1, y + 1))

    #draw the main text on top
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
def reset_game():
    pipe_group.empty()
    flower_group.empty()
    bad_flower_group.empty()
    flappy.rect.x = 200
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

def check_revival():
    #check if the player has enough fresh flowers for revival
    if number_of_flowers >= 1:
        return True
    return False

def revive_cat():
    #revive the cat by setting game_over to False and flying to True
    global game_over, flying, invincible, invincible_start_time
    game_over = False
    flying = True
    invincible = True
    invincible_start_time = pygame.time.get_ticks()
    flappy.rect.y = int(screen_height / 2)

class Cat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"images/cat_{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0  #velocity
        self.clicked = False

    def update(self):

        if flying:
            #gravity
            self.vel += 0.5
            if self.vel > 7:
                self.vel = 7
            if self.rect.bottom < 380:
                self.rect.y += int(self.vel)

        if not game_over:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -8
                jump.play()
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #handle the animation
            self.counter += 1
            flap_cooldown = self.counter / fps

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotate the cat
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/pipe.jpg")
        self.rect = self.image.get_rect()
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2) + 50]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2) + 30]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = flower_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Bad_flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bad_flower_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        #get mouse position
        pos = pygame.mouse.get_pos() #get_pos() returns a small list, [0] -> x, [1] -> y

        #check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1: #get_pos() returns a small list,
                action = True                      #[0] -> left mouse button, [1] -> mid, [2] -> right
                                                   # == 1 -> left mouse button has been clicked
        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

cat_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flower_group = pygame.sprite.Group()
bad_flower_group = pygame.sprite.Group()

flappy = Cat(200, int(screen_height / 2))  #200
cat_group.add(flappy)

#create restart button instance
restart_button = Button(screen_width // 2 - 95, screen_height // 2 - 180, restart_img)
revive_button = Button(screen_width // 2 - 95, screen_height // 2 - 180, revive_img)

run = True
while run:

    clock.tick(fps)
    #draw background
    screen.blit(bg, (0, 0))

    cat_group.draw(screen)
    cat_group.update()
    pipe_group.draw(screen) #like list and have index
    flower_group.draw(screen)
    bad_flower_group.draw(screen)

    #draw the base
    screen.blit(base_img, (base_scroll, 380))


    # Inside the game loop where you check for passing pipes and update the score
    # Check if the cat has passed through a pair of pipes and update the score
    if len(pipe_group) > 0:
        if cat_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and cat_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe:
            if cat_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                print(score)  # Debugging statement to check if the score is being updated
                pass_pipe = False  # Reset pass_pipe after updating score

    #check for collision with flowers
    if pygame.sprite.spritecollideany(flappy, flower_group):
        score += 10
        number_of_flowers += 1
        good.play()
        pygame.sprite.spritecollide(flappy, flower_group, True)

    # check for collision with bad flowers
    if pygame.sprite.spritecollideany(flappy, bad_flower_group):
        score -= 5
        number_of_flowers -= 1
        bad.play()
        pygame.sprite.spritecollide(flappy, bad_flower_group, True)

    #draw the score
    draw_text_white(str(score), font_big, brown, screen_width//2 - 10, 50)

    #draw the number of fresh flowers
    #a bad flower cancels out a fresh flower
    screen.blit(flower_img, (600, 55))
    draw_text_blue(str(number_of_flowers), font_small, white, 650, 60)

    #look for collision, but skip it if invincible
    if not invincible and \
            (pygame.sprite.groupcollide(cat_group, pipe_group, False, False) or \
             flappy.rect.top < 0):
        game_over = True

    #check if cat has hit the base
    if flappy.rect.bottom >= 380:
        game_over = True
        flying = False

    if not game_over and flying:
        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency: #free to create an extra pipe
            pipe_height = random.randint(-150, 0)
            btm_pipe = Pipe(screen_width, (screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, (screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        #generate new flowers
        if time_now - last_flower > pipe_frequency + 500:
            random_x = random.randint(0, 370)
            flower_y = random.randint(100, 200)
            flower = Flower(screen_width + random_x, flower_y)
            flower_group.add(flower)
            last_flower = time_now

        #generate new bad flowers
        if time_now - last_bad_flower > pipe_frequency + 1000:
            random_x = random.randint(370, 740)
            bad_flower_y = random.randint(100, 200)
            bad_flower = Bad_flower(screen_width + random_x, bad_flower_y)
            bad_flower_group.add(bad_flower)
            last_bad_flower = time_now

        #draw and scroll the base
        base_scroll -= scroll_speed
        if abs(base_scroll) > 1673:
            base_scroll = 0

        pipe_group.update()
        flower_group.update()
        bad_flower_group.update()

    #check for invincibility duration
    if invincible and pygame.time.get_ticks() - invincible_start_time > invincible_duration:
        invincible = False

    # check for game over and reset
    if game_over:
        if check_revival():
            if revive_button.draw():
                revive_cat()
                number_of_flowers -= 1 #use one fresh flower to revive the cat
        else:
            if restart_button.draw():
                game_over = False
                score = reset_game()
                number_of_flowers = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    pygame.display.update()

pygame.quit()