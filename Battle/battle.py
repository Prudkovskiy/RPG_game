import random

import pygame
import pyganim
from Battle.Runner_for_battle import *
from pygame import *

from Battle.classes import *

__all__ = ['Bar','LocalUnit', 'Effect', 'BattleScene', 'move', 'vis_attack', 'vis_dead', 'vis_magic',
           'choice', 'animation', 'reset', 'update_bars', 'create_heroes', 'create_enemies', 'check_life', 'main_loop']

class Bar:
    def __init__(self, hero, width=90, height=4):
        self.size = (width, height)
        self.hero = hero
        self.init_hp = hero.hp
        self.init_mp = hero.mp
        self.init_sp = hero.sp

        self.bar_hp = pygame.Surface(self.size)
        self.bar_mp = pygame.Surface(self.size)
        self.bar_sp = pygame.Surface(self.size)

        self.update()

    def update(self):
        self.hp = int((self.hero.hp / self.init_hp) * self.size[0])
        self.mp = int((self.hero.mp / self.init_mp) * self.size[0])
        self.sp = int((self.hero.sp / self.init_sp) * self.size[0])

    def render(self):
        self.bar_hp.fill(Color(128, 128, 128))
        self.bar_hp.fill(Color(255, 0, 0), (0, 0, self.hp, self.size[1]))

        self.bar_mp.fill(Color(128, 128, 128))
        self.bar_mp.fill(Color(65, 105, 225), (0, 0, self.mp, self.size[1]))

        self.bar_sp.fill(Color(128, 128, 128))
        self.bar_sp.fill(Color(255, 99, 71), (0, 0, self.sp, self.size[1]))

        return self.bar_hp, self.bar_mp, self.bar_sp


class LocalUnit():
    def __init__(self, hero_cl, hero_run, type):
        self.hero = hero_run
        self.info = hero_cl
        self.state = 'wait' # 'wait' 'move'
        self.turn = False
        self.type = type
        self.visible = True

        self.init_hp = self.info.hp
        self.init_mp = self.info.mp
        self.init_sp = self.info.sp


class Effect:
    def __init__(self, img, position=(16, 16), width=32, height=32, num=3, lines=1):
        self.img_width = width
        self.img_height = height

        rects = []
        for i in range(lines):
            for n in range(num):
                rects.append((n * width, i * height, width, height))

        all_images = pyganim.getImagesFromSpriteSheet(img, rects=rects)
        frames = list(zip(all_images, [100] * len(all_images)))
        self.anim_objs = pyganim.PygAnimation(frames)

        self.move_conductor = pyganim.PygConductor(self.anim_objs)

        self.pos_x, self.pos_y = position
        self.pos_x -= all_images[0].get_width() / 2
        self.pos_y -= all_images[0].get_height() / 2


    def move(self, dx, dy):
        self.pos_x += dx
        self.pos_y += dy

    def get_pos(self):
        return self.pos_x, self.pos_y


class BattleScene:
    def __init__(self, screen, img, heros = (None, ), enemies = (None, )):
        # Background picture
        self.img_bg = img
        self.screen = screen
        # Heros
        hero_1 = LocalUnit(heros[0][0], heros[1][0], 'hero')
        hero_2 = LocalUnit(heros[0][1], heros[1][1], 'hero')
        hero_3 = LocalUnit(heros[0][2], heros[1][2], 'hero')
        hero_4 = LocalUnit(heros[0][3], heros[1][3], 'hero')
        self.heros = (hero_1, hero_2, hero_3, hero_4)
        #Enemies
        enemy_1 = LocalUnit(enemies[0][0], enemies[1][0], 'enemy')
        enemy_2 = LocalUnit(enemies[0][1], enemies[1][1], 'enemy')
        self.enemies = (enemy_1, enemy_2)
        # Actions menu
        self.buttons_state = 'hero' # 'hero', 'action', 'target'
        self.buttons = ('Attack', 'Magic')
        # Cursor position
        self.cursor_hero = 0
        self.cursor_action = 0
        self.cursor_enemies = 0

        # Bars
        self.bars = (Bar(self.heros[0].info),
                     Bar(self.heros[1].info),
                     Bar(self.heros[2].info),
                     Bar(self.heros[3].info))
        self.en_bars = (Bar(self.enemies[0].info),
                        Bar(self.enemies[1].info))

        # Visual effects
        self.death_act = False
        self.death_animation = Effect('Battle/images/death.png', (100, 100), 96, 96, 12, 1)

        self.attack_act_hero = False
        self.attack_animation_hero = Effect('Battle/images/fireball.png', (100, 100), 64, 64, 8, 1)

        self.attack_act_enemy = False
        self.attack_animation_enemy = Effect('Battle/images/fireball_right.png', (100, 100), 64, 64, 8, 1)

        self.magic_act = False
        self.magic_animation = Effect('Battle/images/magic.png', (100, 100), 128, 128, 8, 7)

        # Pictures
        self.img_bg = pygame.image.load(self.img_bg)
        #self.img_bg = pygame.transform.scale(self.img_bg, self.screen.get_size())
        self.img_menu = pygame.image.load('Battle/images/Frame_dial.png')
        self.img_menu = pygame.transform.scale(self.img_menu, (self.screen.get_size()[0], 130))
        self.img_cur = pygame.image.load('Battle/images/right_small.png')
        self.img_cur = pygame.transform.scale(self.img_cur, (35, 35))
        self.img_cur_left = pygame.image.load('Battle/images/left_small.png')
        self.img_cur_left = pygame.transform.scale(self.img_cur_left, (35, 35))

        self.background = pygame.Surface(self.screen.get_size())


    def render(self):
        self.background.blit(self.img_bg, (0, 0))
        self.background.blit(self.img_menu, (0, self.screen.get_size()[1] - 130))

        # Cursor
        if self.buttons_state == 'hero' and self.cursor_hero != 4: # != 4 - Except done button
            self.background.blit(self.img_cur, (self.screen.get_size()[0] - 330,
                                                self.screen.get_size()[1] - 125 + self.cursor_hero * 25))

        if self.buttons_state == 'hero' and self.cursor_hero == 4: # Done button
            self.background.blit(self.img_cur, (self.screen.get_size()[0] - 105, 25))

        elif self.buttons_state == 'action':
            self.background.blit(self.img_cur, (40,
                                                self.screen.get_size()[1] - 125 + self.cursor_action * 25))

        elif self.buttons_state == 'target':
            if self.enemies[0].info.alive:
                self.background.blit(self.img_cur_left, (self.enemies[self.cursor_enemies].hero.get_pos()[0] + 200,
                                                         self.enemies[self.cursor_enemies].hero.get_pos()[1] + 75))
            else:
                self.background.blit(self.img_cur_left, (self.enemies[1].hero.get_pos()[0] + 200,
                                                         self.enemies[1].hero.get_pos()[1] + 75))

        self.screen.blit(self.background, (0, 0))

        # Hero names
        i = 0
        font = pygame.font.SysFont('Lucida Console', 25)
        for hero in self.heros:
            if hero.visible and not hero.turn:
                color = (255, 255, 255)
            else:
                color = (210, 105, 30)

            text_surface = font.render(hero.info.name.capitalize(), True, color, None)
            self.screen.blit(text_surface, (self.screen.get_size()[0] - 290,
                                            self.screen.get_size()[1] - 118 + 25 * i))


            # Hero health
            if hero.visible:
                s1, s2, s3 = self.bars[i].render()
                self.screen.blit(s1, (self.screen.get_size()[0] - 180,
                                      self.screen.get_size()[1] - 112 + 25 * i))
                self.screen.blit(s2, (self.screen.get_size()[0] - 180,
                                      self.screen.get_size()[1] - 112 + 25 * i + 5))
                self.screen.blit(s3, (self.screen.get_size()[0] - 180,
                                      self.screen.get_size()[1] - 112 + 25 * i + 10))

            # Heros
            if hero.visible:
                if hero.state == 'wait':
                    hero.hero.move_conductor.stop()
                    self.screen.blit(hero.hero.standing[1], hero.hero.get_pos())

                elif hero.state == 'move':
                    hero.hero.move_conductor.play()
                    hero.hero.anim_objs[1].blit(self.screen, hero.hero.get_pos())

            i += 1

        # Menu
        i = 0
        if self.buttons_state == 'action':
            for button in self.buttons:
                text_surface = font.render(button, True, (255, 255, 255), None)
                self.screen.blit(text_surface, (80, self.screen.get_size()[1] - 118 + 25 * i))
                i += 1

        # Done button
        done_button_surface = pygame.image.load('Battle/images/done_button.png')
        self.screen.blit(done_button_surface, (self.screen.get_size()[0] - 64, 20))

        # Enemies
        i = 0
        for enemy in self.enemies:
            if enemy.info.alive:
                enemy.hero.move_conductor.play()
                enemy.hero.anim_objs.blit(self.screen, enemy.hero.get_pos())
                s1, s2, s3 = self.en_bars[i].render()
                self.screen.blit(s1, (enemy.hero.get_pos()[0] + 60,
                                      enemy.hero.get_pos()[1] + 25 * i))
                self.screen.blit(s2, (enemy.hero.get_pos()[0] + 60,
                                      enemy.hero.get_pos()[1] + 25 * i + 5))
                self.screen.blit(s3, (enemy.hero.get_pos()[0] + 60,
                                      enemy.hero.get_pos()[1] + 25 * i + 10))
            i += 1

        # Death animation
        if self.death_act:
            self.death_animation.move_conductor.play()
            self.death_animation.anim_objs.blit(self.screen, self.death_animation.get_pos())
        else:
            self.death_animation.move_conductor.stop()

        # Attack animation
        if self.attack_act_hero:
            self.attack_animation_hero.move_conductor.play()
            self.attack_animation_hero.anim_objs.blit(self.screen,
                                                      self.attack_animation_hero.get_pos())
        else:
            self.attack_animation_hero.move_conductor.stop()

        if self.attack_act_enemy:
            self.attack_animation_enemy.move_conductor.play()
            self.attack_animation_enemy.anim_objs.blit(self.screen,
                                                       self.attack_animation_enemy.get_pos())
        else:
            self.attack_animation_enemy.move_conductor.stop()

        # Magic animation
        if self.magic_act:
            self.magic_animation.move_conductor.play()
            self.magic_animation.anim_objs.blit(self.screen, self.magic_animation.get_pos())
        else:
            self.magic_animation.move_conductor.stop()


def move(scene, hero, direction):
    timer = pygame.time.Clock()

    if hero == 'attack_animation':
        if direction == 1:
            for step in range(20):
                scene.attack_animation_enemy.move(-4, 0)
                scene.attack_animation_hero.move(-4, 0)
                scene.render()
                pygame.display.update()
                timer.tick(60)

        if direction == 'right':
            for step in range(20):
                scene.attack_animation_enemy.move(4, 0)
                scene.attack_animation_hero.move(4, 0)
                scene.render()
                pygame.display.update()
                timer.tick(60)

    elif hero == 'magic_animation':
        if direction == 1:
            for step in range(20):
                scene.magic_animation.move(-4, 0)
                scene.render()
                pygame.display.update()
                timer.tick(60)

        if direction == 'right':
            for step in range(20):
                scene.magic_animation.move(4, 0)
                scene.render()
                pygame.display.update()
                timer.tick(60)

    elif hero.type == 'hero':
        if direction == 1:
            print(hero.state)
            hero.state = 'move'
            print(hero.state)
            for step in range(15):
                hero.hero.move(-4, 0)
                scene.render()
                pygame.display.update()
                timer.tick(60)
            hero.state = 'wait'
            scene.render()
            pygame.display.update()

        if direction == 'right':
            hero.state = 'move'
            for step in range(15):
                hero.hero.move(4, 0)
                scene.render()
                pygame.display.update()
                timer.tick(60)
            hero.state = 'wait'
            scene.render()
            pygame.display.update()

    else:
        if direction == 1:
            for step in range(20):
                hero.hero.move(-4, 0)
                scene.render()
                pygame.display.update()
                timer.tick(60)

        if direction == 'right':
            for step in range(20):
                hero.hero.move(4, 0)
                scene.render()
                pygame.display.update()
                timer.tick(60)


def vis_attack(scene, hero):
    if hero.type == 'hero':
        move(scene, hero, 1)

        scene.attack_animation_hero.pos_x = hero.hero.get_pos()[0] - 40
        scene.attack_animation_hero.pos_y = hero.hero.get_pos()[1] - 5
        scene.attack_act_hero = True
        move(scene, 'attack_animation', 1)
        scene.attack_act_hero = False

        move(scene, hero, 'right')

    else:
        move(scene, hero, 'right')

        scene.attack_animation_enemy.pos_x = hero.hero.get_pos()[0] + 150
        scene.attack_animation_enemy.pos_y = hero.hero.get_pos()[1] + 60
        scene.attack_act_enemy = True
        move(scene, 'attack_animation', 'right')
        scene.attack_act_enemy = False

        move(scene, hero, 1)

def vis_magic(scene, hero):
    if hero.type == 'hero':
        move(scene, hero, 1)

        scene.magic_animation.pos_x = hero.hero.get_pos()[0] - 70
        scene.magic_animation.pos_y = hero.hero.get_pos()[1] - 45
        scene.magic_act = True
        move(scene, 'magic_animation', 1)
        scene.magic_act = False

        move(scene, hero, 'right')

    else:
        move(scene, hero, 'right')

        scene.magic_animation.pos_x = hero.hero.get_pos()[0] + 140
        scene.magic_animation.pos_y = hero.hero.get_pos()[1] + 20
        scene.magic_act = True
        move(scene, 'magic_animation', 'right')
        scene.magic_act = False

        move(scene, hero, 1)


def vis_dead(scene, hero):
    timer = pygame.time.Clock()

    if hero.type == 'hero':
        scene.death_animation.pos_x = hero.hero.get_pos()[0] - 32
        scene.death_animation.pos_y = hero.hero.get_pos()[1] - 32

        scene.death_act = True
        for step in range(3):  # Simple delay
            scene.render()
            pygame.display.update()
            timer.tick(60)
        hero.visible = False
        for step in range(20):  # Simple delay
            scene.render()
            pygame.display.update()
            timer.tick(60)
        scene.death_act = False
        scene.render()
        pygame.display.update()

    else:
        scene.death_animation.pos_x = hero.hero.get_pos()[0] + 70
        scene.death_animation.pos_y = hero.hero.get_pos()[1] + 40

        scene.death_act = True
        for step in range(3):  # Simple delay
            scene.render()
            pygame.display.update()
            timer.tick(60)
        hero.visible = False
        for step in range(20):  # Simple delay
            scene.render()
            pygame.display.update()
            timer.tick(60)
        scene.death_act = False
        scene.render()
        pygame.display.update()


def choice(scene):

    result = ({'action': None, 'target': None, 'turn': None},
              {'action': None, 'target': None, 'turn': None},
              {'action': None, 'target': None, 'turn': None},
              {'action': None, 'target': None, 'turn': None})

    # Check alive heroes
    for hero in scene.heros:
        if hero.info.alive:
            hero.turn = False
        else:
            hero.turn = True

    # Check alive enemies
    num_enemies = 0
    for enemy in scene.enemies:
        if enemy.info.alive:
            num_enemies += 1

    turn = 0
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit('QUIT')
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if scene.buttons_state == 'hero':
                        scene.cursor_hero -= 1
                        if scene.cursor_hero == -1:
                            scene.cursor_hero = 4
                    elif scene.buttons_state == 'action':
                        scene.cursor_action -= 1
                        if scene.cursor_action == -1:
                            scene.cursor_action = 1
                    elif scene.buttons_state == 'target':
                        scene.cursor_enemies -= 1
                        if scene.cursor_enemies == -1:
                            scene.cursor_enemies = num_enemies - 1

                if event.key == pygame.K_DOWN:
                    if scene.buttons_state == 'hero':
                        scene.cursor_hero += 1
                        if scene.cursor_hero == 5:
                            scene.cursor_hero = 0
                    elif scene.buttons_state == 'action':
                        scene.cursor_action += 1
                        if scene.cursor_action == 2:
                            scene.cursor_action = 0
                    elif scene.buttons_state == 'target':
                        scene.cursor_enemies += 1
                        if scene.cursor_enemies == num_enemies:
                            scene.cursor_enemies = 0

                if event.key == pygame.K_RETURN:
                    if scene.cursor_hero == 4:
                        done = True
                    elif not scene.heros[scene.cursor_hero].turn: # Hasn't made his turn yet
                        if scene.buttons_state == 'hero':
                            scene.buttons_state = 'action'
                            scene.cursor_action = 0

                        elif scene.buttons_state == 'action':
                            if scene.cursor_action == 0:
                                result[scene.cursor_hero]['action'] = 'attack'
                            if scene.cursor_action == 1:
                                result[scene.cursor_hero]['action'] = 'magic'
                            scene.buttons_state = 'target'
                            scene.cursor_enemies = 0

                        elif scene.buttons_state == 'target':
                            if scene.enemies[0].info.alive:
                                result[scene.cursor_hero]['target'] = scene.cursor_enemies
                            else:
                                result[scene.cursor_hero]['target'] = 1
                            result[scene.cursor_hero]['turn'] = turn
                            turn += 1
                            scene.buttons_state = 'hero'
                            scene.heros[scene.cursor_hero].turn = True

                if event.key == pygame.K_RIGHT:
                    if scene.buttons_state == 'action':
                        scene.buttons_state = 'hero'
                    if scene.buttons_state == 'target':
                        scene.buttons_state = 'action'


        scene.render()
        pygame.display.update()
    return result


def animation(scene, result, local_player):
    rand_enemy = random.randint(0, 1)

    j = 0
    for turn in range(4):
        # Heroes turn
        i = 0
        for res in result:
            if res['turn'] == turn:
                hero = scene.heros[i]
                target = scene.enemies[result[i]['target']]
                if target.info.alive and hero.info.alive:
                    if res['action'] == 'attack':
                        vis_attack(scene, hero)
                        hero.info.attack(monster=target.info, attack=hero.info.at_list[1])
                        update_bars(scene)
                        if target.info.alive == False:
                            vis_dead(scene, target)
                    elif result[i]['action'] == 'magic':
                        vis_magic(scene, hero)
                        hero.info.attack(monster=target.info, attack=hero.info.at_list[0])
                        update_bars(scene)
                        if target.info.alive == False:
                            vis_dead(scene, target)
            i += 1

        # Enemies turn
        if scene.enemies[rand_enemy].info.alive and j == 0:
            enemy = scene.enemies[rand_enemy]
        elif j < 2:
            enemy = scene.enemies[1 - rand_enemy]
            j = 1
        if j < 2 and enemy.info.alive:
            try:
                alive, hero_name, attack = enemy.info.attack(heroes=local_player.get_alive_heroes())
            except IndexError:
                print('Index Error')
                break
            if attack == 'ph_atk':
                vis_attack(scene, enemy)
            elif attack == 'fire_atk':
                vis_magic(scene, enemy)
            update_bars(scene)
            if alive == False:
                for lh in scene.heros:
                    if lh.info.name == hero_name:
                        vis_dead(scene, lh)
        j += 1


def reset(scene, value):
    for hero in scene.heros:
        hero.info.mp += value
        if hero.info.mp > hero.init_mp:
            hero.info.mp = hero.init_mp
        hero.info.sp += value
        if hero.info.sp > hero.init_sp:
            hero.info.sp = hero.init_sp

    for hero in scene.enemies:
        hero.info.mp += value
        if hero.info.mp > hero.init_mp:
            hero.info.mp = hero.init_mp
        hero.info.sp += value
        if hero.info.sp > hero.init_sp:
            hero.info.sp = hero.init_sp

    update_bars(scene)


def update_bars(scene):
    for bar in scene.bars:
        bar.update()
    for bar in scene.en_bars:
        bar.update()


def create_heroes():
    # From classes.py
    warden_mag_atk = Attack(name='mag_atk', size=20, cost=20, atr_type='mp', defense='mag_def')
    warden_ph_atk = Attack(name='ph_atk', size=10, cost=15, atr_type='sp', defense='ph_def')

    warden_fire_def = Defence(name='fire_def', size=10)
    warden_ph_def = Defence(name='ph_def', size=10)

    hero_1 = Hero(name='usagi', hp=30, mp=50, sp=30, at_list=(warden_mag_atk, warden_ph_atk,),
                  df_list=(warden_fire_def, warden_ph_def,))
    hero_2 = Hero(name='blabla', hp=30, mp=60, sp=30, at_list=(warden_mag_atk, warden_ph_atk,),
                  df_list=(warden_fire_def, warden_ph_def,))
    hero_3 = Hero(name='neko', hp=40, mp=60, sp=70, at_list=(warden_mag_atk, warden_ph_atk,),
                  df_list=(warden_fire_def, warden_ph_def,))
    hero_4 = Hero(name='snake', hp=35, mp=60, sp=40, at_list=(warden_mag_atk, warden_ph_atk,),
                  df_list=(warden_fire_def, warden_ph_def,))

    heros_cl = (hero_1, hero_2, hero_3, hero_4)

    # From Runner.py
    hero_1 = BattlePlayer('images/heros/Usagi.png', (700, 400), 32, 48, 4, 0)
    hero_2 = BattlePlayer('images/heros/Healer.png', (750, 450), 32, 32, 3, 1)
    hero_3 = BattlePlayer('images/heros/Neko.png', (800, 500), 32, 48, 4, 0)
    hero_4 = BattlePlayer('images/heros/Snake.png', (850, 550), 48, 48, 4, 0)

    heros_run = (hero_1, hero_2, hero_3, hero_4)

    return (heros_cl, heros_run)


def create_enemies():
    # From classes.py
    dragon_fire_atk = Attack(name='fire_atk', size=10, cost=20, atr_type='mp', defense='fire_def')
    dragon_ph_atk = Attack(name='ph_atk', size=20, cost=20, atr_type='sp', defense='ph_def')

    dragon_mag_def = Defence(name='mag_def', size=20)
    dragon_ph_def = Defence(name='ph_def', size=10)

    monster_1 = Monster(name='dragon_1', hp=100, mp=50, sp=100, at_list=(dragon_fire_atk, dragon_ph_atk,),
                        df_list=(dragon_ph_def, dragon_mag_def,))
    monster_2 = Monster(name='dragon_2', hp=100, mp=60, sp=70, at_list=(dragon_fire_atk, dragon_ph_atk,),
                        df_list=(dragon_ph_def, dragon_mag_def,))

    enemies_cl = (monster_1, monster_2)

    # From Runner.py
    enemy_1 = BattleEnemy('Battle/images/enemies/reddragonfly.png', (300, 400), 200, 160, 4, 4)
    enemy_2 = BattleEnemy('Battle/images/enemies/yellowdragonfly.png', (200, 500), 200, 160, 4, 4)

    enemies_run = (enemy_1, enemy_2)

    return (enemies_cl, enemies_run)


def check_life(life_cl: list):
    flag = False
    for e in life_cl:
        flag |= e.alive
    return flag

def main_loop():
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('RPG Battle')

    heroes = create_heroes()
    enemies = create_enemies()
    local_player = HelpClass(heroes[0])
    scene = BattleScene(screen, 'images/bg.png', heroes, enemies)

    scene.render()
    pygame.display.update()

    run_game = True
    while run_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit('QUIT')

        result = choice(scene)
        animation(scene, result, local_player)
        reset(scene, 10)

# main_loop()