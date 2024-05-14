import pygame
from pygame import mixer
from pygame.locals import *
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
font = pygame.font.SysFont("Bauhaus 93", 60)

#define colours
brown = (115, 74, 18)

#define game variables(global)
base_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 200
pipe_frequency = 2800 #millise seconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

#load icon
icon = pygame.image.load("images/icon.png")
pygame.display.set_icon(icon)
#load images
bg = pygame.image.load("images/bg.png")
base_img = pygame.image.load("images/base.jpg")
button_img = pygame.image.load("images/start.png")

def draw_text(text, font, tex_col, x, y):
    img = font.render(text, True, tex_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 200
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

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

        if flying == True:
            #gravity
            self.vel += 0.5
            if self.vel > 7:
                self.vel = 7
            if self.rect.bottom < 380:
                self.rect.y += int(self.vel)

        if game_over == False:
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

flappy = Cat(200, int(screen_height / 2))  #200
cat_group.add(flappy)

#create restart button instance
button = Button(screen_width // 2 - 95, screen_height // 2 - 180, button_img)

run = True
while run:

    clock.tick(fps)
    #draw background
    screen.blit(bg, (0, 0))

    cat_group.draw(screen)
    cat_group.update()
    pipe_group.draw(screen) #like list and have index

    #draw the base
    screen.blit(base_img, (base_scroll, 380))

    # Inside the game loop where you check for passing pipes and update the score
    # Check if the cat has passed through a pair of pipes and update the score
    if len(pipe_group) > 0:
        if cat_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and cat_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if cat_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                print(score)  # Debugging statement to check if the score is being updated
                pass_pipe = False  # Reset pass_pipe after updating score

    #draw the score
    draw_text(str(score), font, brown, screen_width//2 - 10, 50)

    #look for collision
    if pygame.sprite.groupcollide(cat_group, pipe_group, False, False)\
            or flappy.rect.top < 0:
        game_over = True

    #check if cat has hit the base
    if flappy.rect.bottom >= 380:
        game_over = True
        flying = False

    if game_over == False and flying == True:
        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency: #free to create an extra pipe
            pipe_height = random.randint(-150, 0)
            btm_pipe = Pipe(screen_width, (screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, (screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        #draw and scroll the base
        base_scroll -= scroll_speed
        if abs(base_scroll) > 50:
            base_scroll = 0

        pipe_group.update()


    #check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

pygame.quit()