import pygame
from core.colors import *
from core.gui_object import *
from projectiles import *
from core.math import angle_between_delta
from core.image import load_image
from core.game_object import GameObject

class Tower(GameObject):
	def __init__(self, tower_type, row, col, game):
		self.PRICE_FONT = pygame.font.SysFont("ComicSansMs", 15)
		super().__init__("towers/tower" + str(tower_type) + "L" + str(1), (col * 64 + 32, row * 64 + 32))
		self.type, self.row, self.col, self.level, self.last_reload_time = tower_type, row, col, 1, 0
		self.max_level = game.tower_max_levels[self.type - 1]
		self.bullets: list[Projectile] = []

		if not self.is_plane():
			self.platform = GameObject("towers/tower" + str(self.type) + "platform" + str(self.level), self.pos)

	def is_plane(self):
		return self.type == 4

	def is_max_level(self):
		return self.level >= self.max_level

	def upgrade(self, mouse_pos, game):	
		if self.is_plane() or self.is_max_level() or game.money < self.price or not pygame.Rect(self.pos.x - 72, self.pos.y - self.range - 74, 50, 50).collidepoint(mouse_pos):
			return

		self.level += 1
		game.money -= self.price
		game.selected_tower = self

	def sell(self, mouse_pos, game):
		if self.is_plane() or game.selected_tower != self:
			return
		
		if pygame.Rect(self.pos.x + 40, self.pos.y - self.range - 54, 50, 50).collidepoint(mouse_pos):			
			game.increase_money(self.sell_price)
			game.towers.remove(self)

	def update_and_draw(self, game):
		#-# Tower Features #-#
		# self.load_image()
		self.range =  game.tower_ranges [self.type - 1][self.level - 1]
		self.damage = game.tower_damages[self.type - 1][self.level - 1]
		self.speed =  game.tower_speeds [self.type - 1][self.level - 1]

		self.now = pygame.time.get_ticks()
		if self.type == 2:
			self.image = load_image("towers/tower" + str(self.type) + "L" + str(self.level) + "_")
			if self.now - self.last_reload_time > self.speed - 1000:
				self.image = load_image("towers/tower" + str(self.type) + "L" + str(self.level))

		if self.is_plane():
			self.move_plane(game.window, game)
		else:
			self.platform.draw(game.window)

		if self.is_selected(game):
			self.draw_range(game.window)

			if not self.is_plane():
				self.draw_selected(game.window, game)

		self.work(game)

		#if self.type == 3 or (self.type == 2 and self.level == 3):
		#	self.rect[1] -= 20

		self.draw(game.window)

	def is_selected(self, game) -> bool:
		return game.selected_tower == self

	def move_plane(self, surface, game):
		self.level = game.plane_level
		self.shadow = load_image("towers/tower" + str(self.type) + "shadow" + str(self.level) + "")
		if game.is_game_started == True and self.pos.x <= 1125:
			self.pos.x += self.speed
			self.column = (self.pos.x // 64)
		surface.blit(self.shadow, (self.pos.x - 20, self.pos.y + 20))

	def draw_range(self, surface):
		self.surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA, 32) 
		pygame.draw.circle(self.surface, (128, 128, 128, 120), (int(self.range), int(self.range)), int(self.range), 0)				
		pygame.draw.circle(self.surface, (0, 200, 0, 120),     (int(self.range), int(self.range)), int(self.range), 2)		
		surface.blit(self.surface, (self.pos.x - self.range, self.pos.y - self.range))

	def draw_selected(self, surface, game):
		self.sell_button    = GUI_Object("", self.pos + Vector2(20,  -110), (50, 50), ("button","sell"))
		self.upgrade_button = GUI_Object("", self.pos + Vector2(-55, -105), (50, 50), ("button", "upgrade"))
		self.max_button     = GUI_Object("", self.pos + Vector2(-60, -85), (50, 25), ("button","max"))

		self.sell_price = surface.tower_sell_prices[self.type - 1][self.level - 1]
		self.sell_price_text = self.PRICE_FONT.render(str(self.sell_price) + " $", 2, White)

		if self.is_max_level():
			self.max_button.draw(surface)
		else:
			self.price = game.tower_sell_prices[self.type - 1][self.level]
			self.price_text = self.PRICE_FONT.render(str(self.price) + " $", 2, White)
			surface.blit(self.price_text, self.pos + Vector2(-50, - 60))
			self.upgrade_button.draw(surface)

		surface.blit(self.sell_price_text, self.pos + Vector2(30, - 60))
		self.sell_button.draw(surface)

	def work(self, game):
		if game.is_game_started != True or game.enemies == [] or self.is_plane():
			return
		
		distances: list[Vector2] = [enemy.pos - self.pos for enemy in game.enemies]
		lengths  : list[float]   = [dist.length() for dist in distances]
		nearest_distance = min(lengths)
		nearest_enemy_index = lengths.index(nearest_distance)
		the_nearest_enemy_distance = distances[nearest_enemy_index]

		if not self.is_in_range(nearest_distance):
			return
		
		self.rotate_to_angle(angle_between_delta(the_nearest_enemy_distance))

		if self.is_attack_ready():
			self.shoot(game.enemies[nearest_enemy_index])

	def is_in_range(self, distance: float) -> bool:
		return distance <= self.range

	def is_attack_ready(self) -> bool:
		self.now = pygame.time.get_ticks()
		return self.now - self.last_reload_time > self.speed

	def shoot(self, target) -> None:
		self.bullet = Projectile(target, self)
		self.bullets.append(self.bullet)
		self.last_reload_time = self.now
