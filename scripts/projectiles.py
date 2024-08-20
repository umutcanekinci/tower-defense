import pygame
from pygame.math import Vector2
from math import atan2, degrees
class Projectile(object):
	def __init__(self, Target, Tower, Angle):
		self.X, self.Y, self.Type, self.Target, self.Tower, self.Damage, self.Speed, self.Angle = Tower.X, Tower.Y, [Tower.Type, Tower.Level], Target, Tower, Tower.damage, Vector2(0, -2), Angle
		self.Image = pygame.image.load("images/bullets/"+str(self.Type[0])+"L"+str(self.Type[1])+".png").convert_alpha()
		self.Pos = Vector2(self.X + 32, self.Y + 32)

	def Move(self, Game):
		
		if Game.enemies != []:
			for self.Enemy in Game.enemies:
				if self.Enemy.Number == self.Target.Number:
					self.Target = self.Enemy
		
		#-# Calculate Distance Between Target And Bullet #-#
		self.DistanceX = self.X - self.Target.X
		self.DistanceY = self.Y - self.Target.Y
		self.Distance = (abs(self.DistanceX)**2 + abs(self.DistanceY)**2)**(1 / 2)

		#-# Rotate the Tower to the Enemys #-#
		self.Radian = atan2(-self.DistanceY, self.DistanceX)
		self.Angle = degrees(self.Radian) + 90

	    #-# Rotate the Tower It's Last Angle #-#
		self.Rect = self.Image.get_rect(center = self.Pos)
		self.RotatedImage = pygame.transform.rotate(self.Image, self.Angle)
		self.Rect = self.RotatedImage.get_rect(center = self.Rect.center)
		self.X, self.Y = self.Rect.x, self.Rect.y

		self.Velocity = Vector2(0, -1).rotate(-self.Angle) * 16
		if self.Distance <= 15:
			self.Tower.Bullets.remove(self)	
			self.Target.DecreaseHP(self.Damage, Game)
		#elif self.Distance%16 == 0:
		#	self.Velocity %= self.Pos
		#	self.Pos += self.Velocity
		else:
			self.Pos += self.Velocity*Game.speed

	def Draw(self, surface):		
		surface.blit(self.RotatedImage, self.Rect)

