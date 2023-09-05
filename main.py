import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer Game")
WIDTH, HEIGHT = 1000,800
FPS = 60
PLAYER_VELOCITY = 5
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    """Just flips the image horizontally"""
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    """
    Loads and crops the sprite sheet containing multiple images
    """
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rectangle = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rectangle)
            sprites.append(pygame.transform.scale2x(surface))
    
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites


    return all_sprites


class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 1

    def __init__(self,x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_velocity = 0
        self.y_velocity = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
    
    def move(self, dx, dy):
        """
        Moves the Player
        """
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, velocity):
        """
        Moves the Player to the left
        """
        self.x_velocity = -velocity
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, velocity):
        """
        Moves the Player to the right
        """
        self.x_velocity = velocity
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    
    def loop(self, fps):
        """
        Loop Function Handles all the things related to our Player like Jumping,
        Animation, etc. and It will be called on every frame
        """
        # self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)
        self.fall_count += 1
        self.update_sprite()

    def update_sprite(self):
        """
        Makes the Animation for sprite in idle state
        """
        sprite_sheet = "idle"
        if self.x_velocity != 0:
            sprite_sheet = "run"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    
    def update(self):
        """
        Makes the rectangle around the sprite as per the sprite kind of masking
        """
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win):
        """
        Draws Something on the Screen
        """
        win.blit(self.sprite, (self.rect.x, self.rect.y))


def get_background(name):
    """
    Designs to fill the Background on the full Screen
    """
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect() # here the two underscores are x and y we do not need those so we are using underscores here
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            position = (i * width, j * height)
            tiles.append(position)
    return tiles, image

def draw(win, background, bg_image, player):
    """
    Draws the tiles on the Screen
    """
    for tile in background:
        win.blit(bg_image, tile)
    
    player.draw(win)
    pygame.display.update()


def handle_movement(player):
    """
    Handles the movement of the Player
    """
    keys = pygame.key.get_pressed()

    player.x_velocity = 0
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VELOCITY)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VELOCITY)


def main():
    """
    Main game function containing main gameloop
    """
    run = True
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    player = Player(100,100,50,50)
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        player.loop(FPS)
        handle_movement(player)
        draw(WINDOW, background, bg_image, player)
    pygame.quit()
    quit()


if __name__ == '__main__':
    main()