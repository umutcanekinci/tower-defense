import pygame as pg
from pygame.math import Vector2


BACKGROUND_COLOR = pg.Color(30, 30, 50)
BLUE = pg.Color('dodgerblue1')
LIME = pg.Color(192, 255, 0)


class Bullet(pg.sprite.Sprite):
    """ This class represents the bullet. """

    def __init__(self, pos, target, screen_rect):
        """Take the pos, direction and angle of the player."""
        super().__init__()
        self.image = pg.Surface((16, 10), pg.SRCALPHA)
        pg.draw.polygon(self.image, LIME, ((0, 0), (16, 5), (0, 10)))
        # The `pos` parameter is the center of the bullet.rect.
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)  # The position of the bullet.
        self.target = target
        # This vector points from the mouse pos to the target.
        direction = target - pos
        # The polar coordinates of the direction vector.
        radius, angle = direction.as_polar()
        # Rotate the image by the negative angle (because the y-axis is flipped).
        self.image = pg.transform.rotozoom(self.image, -angle, 1)
        # The velocity is the normalized direction vector scaled to the desired length.
        self.velocity = direction.normalize() * 11
        self.screen_rect = screen_rect

    def update(self):
        """Move the bullet."""
        self.position += self.velocity  # Update the position vector.

        print("position:",  self.position, "target:", self.target)
        self.rect.center = self.position  # And the rect.

        # Remove the bullet when it leaves the screen.
        if not self.screen_rect.contains(self.rect):
            self.kill()


def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    screen_rect = screen.get_rect()

    clock = pg.time.Clock()

    all_sprites = pg.sprite.Group()
    bullet_group = pg.sprite.Group()

    target = Vector2(400, 300)

    done = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                # Shoot a bullet. Pass the start position (in this
                # case the mouse position) and the direction vector.

                bullet = Bullet(event.pos, target, screen_rect)
                all_sprites.add(bullet)
                bullet_group.add(bullet)

        all_sprites.update()

        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)
        pg.draw.rect(screen, BLUE, (target, (3, 3)), 1)
        pg.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
    pg.quit()