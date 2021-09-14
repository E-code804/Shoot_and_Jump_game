import pygame
import os
import time
import random

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game 1")

start = 0
end = 0

# Load the images
char_left = [pygame.image.load("L1.png"), pygame.image.load("L2.png"), pygame.image.load("L3.png"),
             pygame.image.load("L4.png"), pygame.image.load("L5.png"), pygame.image.load("L6.png"),
             pygame.image.load("L7.png"), pygame.image.load("L8.png"), pygame.image.load("L9.png")]
char_right = [pygame.image.load("R1.png"), pygame.image.load("R2.png"), pygame.image.load("R3.png"),
              pygame.image.load("R4.png"), pygame.image.load("R5.png"), pygame.image.load("R6.png"),
              pygame.image.load("R7.png"), pygame.image.load("R8.png"), pygame.image.load("R9.png")]

e1_img = pygame.image.load("zora.png")
explo = pygame.image.load("explosion.png")
kami = pygame.image.load("pterodactyl.png")
bullet = pygame.transform.scale(pygame.image.load('pixel_laser_yellow.png'), (50, 50))
fire = pygame.transform.scale(pygame.image.load('fire.png'), (100, 70))
bg = pygame.transform.scale(pygame.image.load("BG.png"), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img, dir, up):
        self.x = x
        self.y = y
        self.img = img
        self.dir = dir
        self.up = up
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x + 5, self.y + 14))

    def move(self, vel):
        if not self.up:
            if self.dir:
                self.x -= vel
            else:
                self.x += vel
        else:
            self.y -= vel

    def off_screen(self, width):
        return not (self.x <= width + 300 and self.x + 50 >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Character:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.vel = 5
        self.isJump = False
        self.jumpCount = 10
        self.left = False
        self.right = False
        self.walkCount = 0
        self.health = health
        self.char_img = None
        self.laser_img = bullet
        self.lasers = []
        self.cool_down_counter = 0
        self.COOLDOWN = 7

    def draw(self, window):
        if self.walkCount + 1 >= 27:
            self.walkCount = 0
        if self.left:
            win.blit(char_left[self.walkCount // 3], (self.x, self.y))
            self.walkCount += 1
        elif self.right:
            win.blit(char_right[self.walkCount // 3], (self.x, self.y))
            self.walkCount += 1
        else:
            win.blit(pygame.image.load('standing.png'), (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(800):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 34
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self, up):
        if not up:
            if self.cool_down_counter == 0:
                laser = Laser(self.x, self.y, self.laser_img, self.left, False)
                self.lasers.append(laser)
                self.cool_down_counter = 1
        else:
            if self.cool_down_counter == 0:
                laser = Laser(self.x, self.y, self.laser_img, self.left, True)
                self.lasers.append(laser)
                self.cool_down_counter = 1

    def get_width(self):
        return self.char_img.get_width()

    def get_height(self):
        return self.char_img.get_height()


class Player(Character):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.char_img = pygame.image.load("standing.png")
        self.laser_img = bullet
        self.mask = pygame.mask.from_surface(self.char_img)
        self.max_health = health

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def move_lasers(self, vel, objs, objs2):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 25
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                for obj in objs2:
                    if laser.collision(obj):
                        obj.health -= 100
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (WIDTH - 135, 23, 64, 10))
        pygame.draw.rect(window, (0, 255, 0),
                         (WIDTH - 135, 23, self.char_img.get_width() * (self.health / self.max_health), 10))


class Enemy1(Character):
    def __init__(self, x, y, fly, health=100):
        super().__init__(x, y, health)
        self.fly = fly
        self.char_img = e1_img
        self.laser_img = fire
        self.jumpCount = 5
        self.mask = pygame.mask.from_surface(self.char_img)
        self.COOLDOWN = 50

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        # depending on location will determine which direction shots go in
        if self.cool_down_counter == 0:
            if self.x - WIDTH / 2 < 0:
                laser = Laser(self.x - 20, self.y, self.laser_img, False, None)
            else:
                laser = Laser(self.x - 20, self.y, self.laser_img, True, None)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, obj, dir):
        self.cooldown()
        if not dir:
            for laser in self.lasers:
                laser.move(vel)
                if laser.off_screen(800):
                    self.lasers.remove(laser)
                elif laser.collision(obj):
                    obj.health -= 34
                    self.lasers.remove(laser)
        else:
            for laser in self.lasers:
                if not laser.dir:
                    laser.x += vel
                    laser.y += vel
                elif laser.dir:
                    laser.x -= vel
                    laser.y += vel
                if laser.off_screen(800):
                    self.lasers.remove(laser)
                elif laser.collision(obj):
                    obj.health -= 34
                    self.lasers.remove(laser)


    def draw(self, window):
        if not self.fly:
            window.blit(self.char_img, (self.x, self.y))
        else:
            if self.jumpCount >= -5:
                neg = 1
                if self.jumpCount < 0:
                    neg = -1
                self.y -= (self.jumpCount ** 2) * 0.5 * neg
                self.jumpCount -= 0.5
            else:
                self.jumpCount = 5
            window.blit(self.char_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)


class Enemy2(Character):
    def __init__(self, x, y, fall, health=100):
        super().__init__(x, y, health)
        self.char_img = kami
        self.fall = fall
        self.mask = pygame.mask.from_surface(self.char_img)
        self.COOLDOWN = 20

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def draw(self, window):
        self.cooldown()
        if self.cool_down_counter == 0:
            self.y += self.fall
            window.blit(kami, (self.x, self.y - self.fall))



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) is not None


def main():
    run = True
    FPS = 30
    level = 0
    en_height = 0
    lost = False
    lost_count = 0
    main_font = pygame.font.SysFont("comicsans", 50)

    enemies = []
    enemies2 = []
    #make an explo list and follow same path as the for loops in redraw, migtht make new class.
    en1_length = 2
    en2_length = 0

    player = Player(400, 430)
    vel = 10

    clock = pygame.time.Clock()

    def redraw_win():
        win.blit(bg, (0, 0))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        health_label = main_font.render("Health:", 1, (255, 255, 255))

        win.blit(level_label, (10, 10))
        win.blit(health_label, (WIDTH - health_label.get_width() - 150, 10))

        player.draw(win)
        for enemy in enemies:
            enemy.draw(win)

        for enemy in enemies2:
            enemy.draw(win)

        if lost:
            lost_label = main_font.render("You Lost!!", 1, (0, 0, 0))
            retry_label = main_font.render("Press the mouse if you want to play again:", 1, (0, 0, 0))
            win.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 200))
            win.blit(retry_label, (WIDTH / 2 - retry_label.get_width() / 2, 300))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    main_menu()
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_win()

        if player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0 and len(enemies2) == 0:
            level += 1
            vel += 0.2
            if player.health < 100:
                player.health = 100
            if level % 5 == 0:
                en1_length += 2
                vel = 10
            if level % 2 == 0:
                en2_length += 1
            for i in range(en1_length):
                en_height += 60
                if i % 2 == 0:
                    if len(enemies) < 2:
                        enemy = Enemy1(0, HEIGHT - en_height - 60, False)
                    else:
                        enemy = Enemy1(0, HEIGHT - en_height - 60, True)
                    enemies.append(enemy)
                else:
                    if len(enemies) < 2:
                        enemy = Enemy1(WIDTH - 120, HEIGHT - en_height, False)
                    else:
                        enemy = Enemy1(WIDTH - 120, HEIGHT - en_height, True)
                    enemies.append(enemy)
            en_height = 0
            for i in range(en2_length):
                enemy = Enemy2(random.randrange(125, WIDTH - 100), -40 - en_height, 5)
                enemies2.append(enemy)
                en_height += 100
            en_height = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            player.shoot(False)
        if keys[pygame.K_a] and player.x - player.vel > 0:  # left
            player.x -= player.vel
            player.left = True
            player.right = False
        if keys[pygame.K_d] and player.x + player.vel + player.get_width() - 60 < WIDTH:  # right
            player.x += player.vel
            player.left = False
            player.right = True
        if keys[pygame.K_d] == 0 and keys[pygame.K_a] == 0:
            player.left = False
            player.right = False
            player.walkCount = 0
        if keys[pygame.K_e]:
            player.shoot(True)

        if not (player.isJump):
            if keys[pygame.K_w]:  # add another jump button that does not go so high
                player.isJump = True
                player.right = False
                player.left = False
                player.walkCount = 0
        else:
            if player.jumpCount >= -10:
                neg = 1
                if player.jumpCount < 0:
                    neg = -1
                player.y -= (player.jumpCount ** 2) * 0.5 * neg
                player.jumpCount -= 1
            else:
                player.isJump = False
                player.jumpCount = 10
        for enemy in enemies[:]:
            # create of boolean to switch where the shots go
            if enemies.index(enemy) < 4:
                enemy.move_lasers(vel, player, False)
            else:
                enemy.move_lasers(vel, player, True)
            if collide(enemy, player):
                player.health -= 34
                # if we are hit by enemy sprite, move away 100 pixels so do not insta die
                # maybe add cooldown here
                if player.left:
                    player.x += 100
                elif player.right:
                    player.x -= 100
            if enemy.health == 0:
                enemies.remove(enemy)
            if random.randrange(0, 0.75 * 60) == 1:
                enemy.shoot()

        for enemy in enemies2:
            if collide(enemy, player):
                player.health -= 34
                enemies2.remove(enemy)
            elif enemy.y >= 450 or enemy.health == 0:
                enemies2.remove(enemy)
        player.move_lasers(vel, enemies, enemies2)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        win.blit(bg, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (0, 0, 0))
        win.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 200))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
