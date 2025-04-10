"""
sprites.py
This module defines classes for handling 2D sprites and animated sprites in a game using Pygame.
"""
from pathlib import Path
import pygame
from misc import scale, rotoscale


class Sprite:
    """
    Represents a 2D sprite that can be drawn on a surface.

    Attributes:
        texture (pygame.Surface): The texture of the sprite.
    """

    def __init__(self, texture_file, uv=None, wh=None):
        """
        Initializes a Sprite object.

        Args:
            texture_file (str or pygame.Surface): The file path to the texture or a preloaded surface.
            uv (tuple, optional): The top-left corner of the subsurface (x, y). Defaults to None.
            wh (tuple, optional): The width and height of the subsurface. Defaults to None.
        """
        if isinstance(texture_file, str):
            asset_folder = Path(__file__).resolve().with_name("assets")
            self.texture = pygame.image.load(asset_folder.joinpath(texture_file)).convert_alpha()
            if uv is not None:
                self.texture = self.texture.subsurface(uv[0], uv[1], wh[0], wh[1])
        else:
            if uv is None:
                self.texture = texture_file
            else:
                self.texture = texture_file.subsurface(uv[0], uv[1], wh[0], wh[1])

    def draw(self, surface, position, size=None, angle=0, alpha=255):
        """
        Draws the sprite on a given surface.

        Args:
            surface (pygame.Surface): The surface to draw the sprite on.
            position (tuple): The (x, y) position to draw the sprite.
            size (tuple, optional): The size to scale the sprite to. Defaults to the original size.
            angle (float, optional): The angle to rotate the sprite. Defaults to 0.
            alpha (int, optional): The alpha value for transparency. Defaults to 255 (opaque).
        """
        if alpha != 255:
            self.texture.set_alpha(alpha)
        if size is None:
            size = self.texture.get_size()
        if angle != 0:
            rotated = rotoscale(self.texture, angle, size)
            position = rotated.get_rect(center=position)
            surface.blit(rotated, position)
        else:
            surface.blit(scale(self.texture, size), position)


class AnimatedSprite:
    """
    Represents an animated sprite composed of multiple frames.

    Attributes:
        sprite_sheet (Sprite): The sprite sheet containing all frames.
        sprites (list): A list of individual frame sprites.
        current_frame (int): The index of the current frame.
        frame_time (float): The time elapsed since the last frame change.
        animation_time (float): The time duration for each frame.
    """

    def __init__(self, texture_file, uvs=None, wh=None, ft=-1):
        """
        Initializes an AnimatedSprite object.
        Args:
            texture_file (str or pygame.Surface or AnimatedSurface): The file path to the texture or
            a preloaded surface or AnimatedSprite object.
            uvs (list, optional): A list of tuples representing the top-left corners of each frame.
            wh (list, optional): A list of tuples representing the width and height of each frame.
            ft (float, optional): The time duration for each frame. Defaults to -1.
        """
        if isinstance(texture_file, AnimatedSprite):
            self.sprite_sheet = texture_file.sprite_sheet
            self.sprites = texture_file.sprites
            self.current_frame = 0
            self.frame_time = 0
            self.animation_time = texture_file.animation_time
            return
        self.sprite_sheet = Sprite(texture_file)
        self.sprites = [Sprite(self.sprite_sheet.texture, uv=uv, wh=wh) for uv in uvs]
        self.current_frame = 0
        self.frame_time = 0
        self.animation_time = ft

    def copy(self):
        """
        Creates a copy of the AnimatedSprite object.

        Returns:
            AnimatedSprite: A new instance of AnimatedSprite with the same properties.
        """
        return AnimatedSprite(self)

    def update(self, dt):
        """
        Updates the animation by advancing the frame based on elapsed time.

        Args:
            dt (float): The time elapsed since the last update, in seconds.
        """
        if self.animation_time <= 0:
            return
        self.frame_time += dt
        while self.frame_time >= self.animation_time:
            self.frame_time -= self.animation_time
            self.next_frame()

    def set_frame(self, frame):
        """
        Sets the current frame of the animation.

        Args:
            frame (int): The index of the frame to set as current.
        """
        if 0 <= frame < len(self.sprites):
            self.current_frame = frame
        else:
            raise ValueError("Frame index out of range")

    def next_frame(self):
        """
        Advances to the next frame in the animation.
        """
        self.current_frame = (self.current_frame + 1) % len(self.sprites)

    def draw(self, surface, position, size=None, angle=0, alpha=255):
        """
        Draws the current frame of the animated sprite on a given surface.

        Args:
            surface (pygame.Surface): The surface to draw the sprite on.
            position (tuple): The (x, y) position to draw the sprite.
            size (tuple, optional): The size to scale the sprite to. Defaults to the original size.
            angle (float, optional): The angle to rotate the sprite. Defaults to 0.
            alpha (int, optional): The alpha value for transparency. Defaults to 255 (opaque).
        """
        self.sprites[self.current_frame].draw(surface, position, size, angle, alpha)
