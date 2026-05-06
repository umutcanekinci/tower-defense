from typing import Union
import os
import pygame
from pygame_core.asset_path import ImagePath
from pygame_core.unity.gameobject import GameObject
from pygame_core.unity.components.sprite_renderer2d import SpriteRenderer2D
from pygame_core.utils import MouseInteractive

PathLike = Union[str, ImagePath, os.PathLike]

class ImageObject(GameObject, MouseInteractive):
	def __init__(self, path: PathLike, pos: tuple[int, int],
	             size: tuple[int, int] = (0, 0),
				 nine_slice: int = 0) -> None:
		super().__init__()

		image = self.load(path, size, nine_slice)
		renderer = self.add_component(SpriteRenderer2D)
		renderer.set_image(image)
		self.rect.size = image.get_size()
		self.rect.topleft = pos

	def load(self, path, size, nine_slice):
		loaded = ImageLoader.load(path)

		if size == (0, 0):
			return loaded

		if nine_slice > 0 :
			return ImageLoader.nine_slice_scale(loaded, size, nine_slice)

		return ImageLoader.scale_surface(loaded, size)

class ImageLoader:
	# def load(path: str, extension=".png"):
	# 	if path is None:
	# 		return None
	# 	return pygame.image.load("assets/images/" + path + extension).convert_alpha()

	def load(path, size=None, return_size=False):
		img = pygame.image.load(path).convert_alpha()

		if size is None:
			size = [0, 0]
		elif isinstance(size, tuple):
			size = list(size)

		if size == [0, 0]:
			return (img, list(img.get_size())) if return_size else img

		if size[0] == 0:   size[0] = img.get_width()
		if size[1] == 0:   size[1] = img.get_height()
		if size[0] == 1 / 3: size[0] = img.get_width() // 5
		if size[1] == 1 / 3: size[1] = img.get_height() // 5

		scaled = pygame.transform.scale(img, size)
		return (scaled, size) if return_size else scaled

	def scale_surface(image, size):
		return pygame.transform.scale(image, size)

	def nine_slice_scale(image: pygame.Surface, target_size: tuple[int, int], corner: int) -> pygame.Surface:
		"""Scale image to target_size using 9-slice.

		corner: size of the corner region in the SOURCE image (pixels).
		Corners are copied at their original pixel size (no distortion).
		Edges are stretched in one axis; the center fills the remaining area.
		Uses nearest-neighbour (pygame.transform.scale) to keep pixel art crisp.
		"""
		src_w, src_h = image.get_size()
		dst_w, dst_h = target_size
		result = pygame.Surface(target_size, pygame.SRCALPHA)

		msx = src_w - corner * 2  # mid width  in source
		msy = src_h - corner * 2  # mid height in source
		mdx = dst_w - corner * 2  # mid width  in dest
		mdy = dst_h - corner * 2  # mid height in dest

		def _blit(sx, sy, sw, sh, dx, dy, dw, dh):
			piece = image.subsurface((sx, sy, sw, sh))
			if (sw, sh) != (dw, dh):
				piece = pygame.transform.scale(piece, (dw, dh))
			result.blit(piece, (dx, dy))

		c = corner
		sw, sh = src_w, src_h
		dw, dh = dst_w, dst_h

		# corners (no scaling)
		_blit(0, 0, c, c, 0, 0, c, c)
		_blit(sw - c, 0, c, c, dw - c, 0, c, c)
		_blit(0, sh - c, c, c, 0, dh - c, c, c)
		_blit(sw - c, sh - c, c, c, dw - c, dh - c, c, c)
		# edges (stretch in one axis)
		_blit(c, 0, msx, c, c, 0, mdx, c)
		_blit(c, sh - c, msx, c, c, dh - c, mdx, c)
		_blit(0, c, c, msy, 0, c, c, mdy)
		_blit(sw - c, c, c, msy, dw - c, c, c, mdy)
		# center (stretch in both axes)
		_blit(c, c, msx, msy, c, c, mdx, mdy)

		return result