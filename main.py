import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer Game")
WIDTH, HEIGHT = 1000, 800
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
            surface.blit(sprite_sheet, (0, 0), rectangle)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def load_block(size):
    """
    Loads the Block from the spritesheet present in the local directory
    """
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    # Here 96, 0 are the coordinates from where we have to load the image from the spritesheet. If you want to use a different terrain image you have to change these numbers accordingly.
    rectangle = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rectangle)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_velocity = 0
        self.y_velocity = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

    def jump(self):
        """
        Makes the Player Jump
        """
        self.y_velocity = - self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
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
        self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        """
        Resets the fall count, y velocity and jump count to zero as the player has landed
        """
        self.fall_count = 0
        self.y_velocity = 0
        self.jump_count = 0

    def hit_head(self):
        """
        If the player has hit the floor with the head
        """
        self.count = 0
        self.y_velocity *= -1

    def update_sprite(self):
        """
        Makes the Animation for sprite in idle state
        """
        sprite_sheet = "idle"
        if self.y_velocity < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"

            elif self.jump_count == 2:
                sprite_sheet = "double_jump"

        elif self.y_velocity > self.GRAVITY * 2:
            sprite_sheet = "fall"

        elif self.x_velocity != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        """
        Makes the rectangle around the sprite as per the sprite kind of masking
        """
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        """
        Draws Something on the Screen
        """
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        """
        Draws objects on the screen
        """
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
    """
    Designs to fill the Background on the full Screen
    """
    image = pygame.image.load(join("assets", "Background", name))
    # here the two underscores are x and y we do not need those so we are using underscores here
    _, _, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            position = (i * width, j * height)
            tiles.append(position)
    return tiles, image


def draw(win, background, bg_image, player, objects, offset_x):
    """
    Draws the tiles on the Screen
    """
    for tile in background:
        win.blit(bg_image, tile)

    for obj in objects:
        obj.draw(win, offset_x)

    player.draw(win, offset_x)
    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    """
    Handles the collision in the vertical direction only
    """
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
        collided_objects.append(obj)

    return collided_objects


def handle_horizontal_collision(player, objects, dx):
    """
    Handles the collision in the horizontal direction only
    """
    player.move(dx, 0)
    # The reason we are updating the player is because we want to update the mask before we check for the collision
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_movement(player, objects):
    """
    Handles the movement of the Player
    """
    keys = pygame.key.get_pressed()

    player.x_velocity = 0

    collide_left = handle_horizontal_collision(player, objects, -PLAYER_VELOCITY * 2)
    collide_right = handle_horizontal_collision(player, objects, PLAYER_VELOCITY * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VELOCITY)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VELOCITY)

    handle_vertical_collision(player, objects, player.y_velocity)


def main():
    """
    Main game function containing main gameloop
    """
    run = True
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")
    block_size = 96

    player = Player(100, 100, 50, 50)
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size)]
    offset_x = 0
    scroll_area_width = 200
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        handle_movement(player, objects)
        draw(WINDOW, background, bg_image, player, objects, offset_x)

        # The below if statement checks if the player is moving to the right
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_velocity > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_velocity < 0):
            offset_x += player.x_velocity
    pygame.quit()
    quit()


if __name__ == '__main__':
    main()
