import pygame
import socket
import math
import time
import os
import threading
import random

from RPG.other import *
from RPG.life import *
from RPG.map import *
from RPG import sql

from RPG.Battle.battle import *
from RPG.Battle.classes import *

from RPG.input_pygame import pygame_textinput


class Game:
    """
    Основной класс игры.
    """

    def __init__(self):
        """
        Pass
        """

        # Флаг работы игры
        self.RUN = True

        # Соккет для UDP соединения
        self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_udp.settimeout(1)
        self.run_udp = False

        # Соккет для TCP соединения
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.settimeout(1)
        self.run_tcp = False

        # Вспомогательные "Флаги"
        self.show_message_frame = True
        self.show_glow = False

        # Окно сообщений
        self.message_frame = Message(font_path='Font/UbuntuMono-R.ttf',
                                     font_size=12,
                                     frame='IMG/Frames/Frame_message.png')

        # Окно настроек
        self.option_frame = pygame.image.load('IMG/Frames/Options.png')

        # Изображение иконок
        self.icon = Game.icon_init()

        # Основное игровое окно
        self.screen = Game.pygame_init()

        # Окно ввода
        self.dial_frame = pygame.image.load('IMG/Frames/Frame_dial.png')

        # Другие игроки
        self.friends = {}

        # Логин игрока
        self.login = ''

        # Основной игрок
        self.current_player = None

        # Номер основного игрока среди героев
        self.num_player = 0

        # Анимация всех героев
        self.players = []

        # Начальная карта
        self.current_map = 'TilesMap/Town.tmx'

        # Класс героев, в отличае от players несет в себе только информацию о характеристиках.
        self.heroes = []

        # Деньги
        self.money = 0

        # Флаг онлайна. Можно сказать объеденение run_tcp и run_udp
        self.online = False

    def connect(self):
        if self.online:
            print('connect')
            self.run_tcp = True
            self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_tcp.settimeout(1)
            try:
                self.sock_tcp.connect((HOST, PORT_TCP))
            except socket.timeout:
                self.run_tcp = False
                self.sock_tcp.close()
                self.online = False
                return
            self.run_udp = True
            self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock_udp.settimeout(1)

    def disconnect(self):
        if self.online:
            self.run_tcp = False
            self.sock_tcp.close()
            self.run_udp = False
            self.sock_udp.close()

    def search_life_hero(self):
        if self.heroes[self.num_player].alive and self.current_player is not None:
            return
        if not self.heroes[self.num_player].alive:
            k = 0
            for k in range(4):
                if self.heroes[k].alive:
                    break
            self.num_player = k
        if self.current_player is None:
            self.current_player = Player(self.login, self.players[self.num_player].key)
        else:
            self.current_player.update_anim(self.players[self.num_player])
            if self.run_tcp:
                self.sock_tcp.send(self.current_player.encode_tcp(4))

    def load_data(self, *args):
        """
        Обработка данных пришедших из сохранения
        :param args: Массив данных из базы данных
        :return: None
        """
        self.current_map = args[2]
        self.players = [Life(args[6]), Life(args[28]), Life(args[50]), Life(args[72])]
        # В будущем сделать выбор живого героя
        self.heroes = [
            Hero(args[5], args[7], args[9], args[11],
                 [Attack(*args[13:18]), Attack(*args[18:23])],
                 [Defence(*args[23:25]), Defence(*args[25:27])]),

            Hero(args[27], args[29], args[31], args[33],
                 [Attack(*args[35:40]), Attack(*args[40:45])],
                 [Defence(*args[45:47]), Defence(*args[47:49])]),

            Hero(args[49], args[51], args[53], args[55],
                 [Attack(*args[57:62]), Attack(*args[62:67])],
                 [Defence(*args[67:69]), Defence(*args[69:71])]),

            Hero(args[71], args[73], args[75], args[77],
                 [Attack(*args[79:84]), Attack(*args[84:89])],
                 [Defence(*args[89:91]), Defence(*args[91:93])])
        ]
        self.current_player = Player(self.login, args[6])
        for h in self.heroes:
            if h.hp <= 0:
                h.alive = False
                h.hp = 0
        self.search_life_hero()
        self.current_player.pos_x = args[3]
        self.current_player.pos_y = args[4]

    def load(self) -> str:
        """
        Страница сохранения
        :return: Строка следующего состояния
        """
        database = sql.DB()
        save = database.all_save()
        save.sort(key=lambda x: x[0])
        if len(save) == 0:
            return 'MENU'

        key = ['noname',
               'actor100', 'actor101', 'actor102', 'actor103', 'actor104', 'actor105', 'actor106', 'actor107',
               'actor200', 'actor201', 'actor202', 'actor203', 'actor204', 'actor205', 'actor206', 'actor207',
               'actor300', 'actor301', 'actor302', 'actor303', 'actor304', 'actor305', 'actor306', 'actor307']
        anim = dict(zip(key, list(map(lambda x: Life(x), key))))

        ind = 0
        offset = 0
        sup_ind = min(3, len(save))
        sup_offset = max(1, len(save) - 2)

        arrow = self.icon['arrow_right']
        arrow_pos = [(220, 112 + y * 256) for y in range(3)]
        frame_right = pygame.image.load('IMG/Frames/Load_1.png')
        frame_left = pygame.image.load('IMG/Frames/Frame_load.png')

        font_object = pygame.font.Font('Font/UbuntuMono-R.ttf', 20)

        while self.RUN:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.RUN = False
                    return 'QUIT'
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        self.load_data(*save[offset + ind])
                        return 'OK'
                    elif e.key == pygame.K_ESCAPE:
                        return 'MENU'
                    elif e.key == pygame.K_DOWN:
                        ind += 1
                        if ind >= sup_ind:
                            ind = sup_ind - 1
                            offset += 1
                            if offset >= sup_offset:
                                offset = sup_offset-1
                        pygame.time.delay(30)
                    elif e.key == pygame.K_UP:
                        ind -= 1
                        if ind < 0:
                            ind = 0
                            offset -= 1
                            if offset < 0:
                                offset = 0
                        pygame.time.delay(30)
            self.screen.fill((0, 0, 0))
            self.screen.blit(frame_right, (0, 0))
            for i in range(sup_ind):
                self.screen.blit(frame_left, (256, i * 256))
                # Hero_1
                # Face
                self.screen.blit(anim[save[i + offset][6]].face[0], (261, 5 + i * 256))
                # Name
                self.screen.blit(
                    font_object.render(save[i + offset][5], True, (255, 255, 255)),
                    (400, 7 + i * 256)
                )
                # HP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][7:9]), True, (255, 255, 255)),
                    (400, 31 + i * 256)
                )
                # MP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][9:11]), True, (255, 255, 255)),
                    (400, 55 + i * 256)
                )
                # SP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][11:13]), True, (255, 255, 255)),
                    (400, 79 + i * 256)
                )

                # Hero_2
                # Face
                self.screen.blit(anim[save[i + offset][28]].face[0], (561, 5 + i * 256))
                # Name
                self.screen.blit(
                    font_object.render(save[i + offset][27], True, (255, 255, 255)),
                    (700, 7 + i * 256)
                )
                # HP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][29:31]), True, (255, 255, 255)),
                    (700, 31 + i * 256)
                )
                # MP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][31:33]), True, (255, 255, 255)),
                    (700, 55 + i * 256)
                )
                # SP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][33:35]), True, (255, 255, 255)),
                    (700, 79 + i * 256)
                )

                # Hero_3
                # Face
                self.screen.blit(anim[save[i + offset][50]].face[0], (261, 133 + i * 256))
                # Name
                self.screen.blit(
                    font_object.render(save[i + offset][49], True, (255, 255, 255)),
                    (400, 135 + i * 256)
                )
                # HP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][51:53]), True, (255, 255, 255)),
                    (400, 159 + i * 256)
                )
                # MP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][53:55]), True, (255, 255, 255)),
                    (400, 183 + i * 256)
                )
                # SP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][55:57]), True, (255, 255, 255)),
                    (400, 207 + i * 256)
                )

                # Hero_4
                # Face
                self.screen.blit(anim[save[i + offset][72]].face[0], (561, 133 + i * 256))
                # Name
                self.screen.blit(
                    font_object.render(save[i + offset][71], True, (255, 255, 255)),
                    (700, 135 + i * 256)
                )
                # HP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][73:75]), True, (255, 255, 255)),
                    (700, 159 + i * 256)
                )
                # MP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][75:77]), True, (255, 255, 255)),
                    (700, 183 + i * 256)
                )
                # SP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][77:79]), True, (255, 255, 255)),
                    (700, 207 + i * 256)
                )

                # Time
                self.screen.blit(
                    font_object.render(save[i + offset][1], True, (255, 255, 255)),
                    (856, 31 + i * 256)
                )
            self.screen.blit(arrow, arrow_pos[ind])
            pygame.display.flip()

        return 'QUIT'

    def save_data(self) -> list:
        """
        Создание данных для сохранения
        :return: Список данных
        """
        i = 0
        buf = []
        for h in self.heroes:
            buf += h.to_list(self.players[i].key)
            i += 1
        return [
            time.strftime("%Y.%m.%d %H:%M"),
            self.current_map, int(self.current_player.pos_x), int(self.current_player.pos_y),
            *buf
        ]

    def save(self) -> str:
        """
        Страница сохранения
        :return: Строка следующего состояния
        """
        database = sql.DB()
        save = database.all_save()
        if len(save) == 0:
            database.new_save(0, self.save_data())
            return 'OK'
        save.sort(key=lambda x: x[0])
        key = ['noname',
               'actor100', 'actor101', 'actor102', 'actor103', 'actor104', 'actor105', 'actor106', 'actor107',
               'actor200', 'actor201', 'actor202', 'actor203', 'actor204', 'actor205', 'actor206', 'actor207',
               'actor300', 'actor301', 'actor302', 'actor303', 'actor304', 'actor305', 'actor306', 'actor307']
        anim = dict(zip(key, list(map(lambda x: Life(x), key))))

        ind = 0
        offset = 0
        sup_ind = min(3, len(save))
        sup_offset = max(1, len(save) - 2)

        arrow = self.icon['arrow_right']
        arrow_pos = [(220, 112 + y * 256) for y in range(3)]
        frame_right = pygame.image.load('IMG/Frames/Save.png')
        frame_left = pygame.image.load('IMG/Frames/Frame_load.png')

        font_object = pygame.font.Font('Font/UbuntuMono-R.ttf', 20)

        while self.RUN:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.RUN = False
                    return 'QUIT'
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        database.override(save[offset+ind][0], self.save_data())
                        return 'OK'
                    elif e.key == pygame.K_SPACE:
                        database.new_save(save[len(save)-1][0]+1, self.save_data())
                        return 'OK'
                    elif e.key == pygame.K_ESCAPE:
                        return 'OK'
                    elif e.key == pygame.K_DOWN:
                        ind += 1
                        if ind >= sup_ind:
                            ind = sup_ind - 1
                            offset += 1
                            if offset >= sup_offset:
                                offset = sup_offset-1
                        pygame.time.delay(30)
                    elif e.key == pygame.K_UP:
                        ind -= 1
                        if ind < 0:
                            ind = 0
                            offset -= 1
                            if offset < 0:
                                offset = 0
                        pygame.time.delay(30)
            self.screen.fill((0, 0, 0))
            self.screen.blit(frame_right, (0, 0))
            for i in range(sup_ind):
                self.screen.blit(frame_left, (256, i * 256))
                # Hero_1
                # Face
                self.screen.blit(anim[save[i + offset][6]].face[0], (261, 5 + i * 256))
                # Name
                self.screen.blit(
                    font_object.render(save[i + offset][5], True, (255, 255, 255)),
                    (400, 7 + i * 256)
                )
                # HP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][7:9]), True, (255, 255, 255)),
                    (400, 31 + i * 256)
                )
                # MP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][9:11]), True, (255, 255, 255)),
                    (400, 55 + i * 256)
                )
                # SP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][11:13]), True, (255, 255, 255)),
                    (400, 79 + i * 256)
                )

                # Hero_2
                # Face
                self.screen.blit(anim[save[i + offset][28]].face[0], (561, 5 + i * 256))
                # Name
                self.screen.blit(
                    font_object.render(save[i + offset][27], True, (255, 255, 255)),
                    (700, 7 + i * 256)
                )
                # HP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][29:31]), True, (255, 255, 255)),
                    (700, 31 + i * 256)
                )
                # MP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][31:33]), True, (255, 255, 255)),
                    (700, 55 + i * 256)
                )
                # SP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][33:35]), True, (255, 255, 255)),
                    (700, 79 + i * 256)
                )

                # Hero_3
                # Face
                self.screen.blit(anim[save[i + offset][50]].face[0], (261, 133 + i * 256))
                # Name
                self.screen.blit(
                    font_object.render(save[i + offset][49], True, (255, 255, 255)),
                    (400, 135 + i * 256)
                )
                # HP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][51:53]), True, (255, 255, 255)),
                    (400, 159 + i * 256)
                )
                # MP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][53:55]), True, (255, 255, 255)),
                    (400, 183 + i * 256)
                )
                # SP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][55:57]), True, (255, 255, 255)),
                    (400, 207 + i * 256)
                )

                # Hero_4
                # Face
                self.screen.blit(anim[save[i + offset][72]].face[0], (561, 133 + i * 256))
                # Name
                self.screen.blit(
                    font_object.render(save[i + offset][71], True, (255, 255, 255)),
                    (700, 135 + i * 256)
                )
                # HP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][73:75]), True, (255, 255, 255)),
                    (700, 159 + i * 256)
                )
                # MP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][75:77]), True, (255, 255, 255)),
                    (700, 183 + i * 256)
                )
                # SP
                self.screen.blit(
                    font_object.render('{}/{}'.format(*save[i + offset][77:79]), True, (255, 255, 255)),
                    (700, 207 + i * 256)
                )

                # Time
                self.screen.blit(
                    font_object.render(save[i + offset][1], True, (255, 255, 255)),
                    (856, 31 + i * 256)
                )
            self.screen.blit(arrow, arrow_pos[ind])
            pygame.display.flip()

        return 'QUIT'

    def menu(self) -> str:
        """
        Отвечает за прорисовку меню
        :return: Строка следующего состояния
        """
        arrow = self.icon['arrow_left']
        arrow_pos = [(955, 395 + x * 47) for x in range(5)]
        i_a = 0
        menu_surface = pygame.image.load('IMG/Frames/Menu.png')
        while self.RUN:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.RUN = False
                    return 'QUIT'
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        if i_a == 0:
                            # Новая игра
                            return 'NEW'
                        elif i_a == 1:
                            # Загрузка
                            return 'LOAD'
                        elif i_a == 2:
                            # Настройки
                            # Пока не добавлены в будущем будет настройка графики.
                            pass
                        elif i_a == 3:
                            # Авторы
                            pass
                        elif i_a == 4:
                            # Выход
                            self.RUN = False
                            return 'QUIT'
                    elif e.key == pygame.K_DOWN:
                        i_a += 1
                        if i_a >= len(arrow_pos):
                            i_a = 0
                        pygame.time.delay(30)
                    elif e.key == pygame.K_UP:
                        i_a -= 1
                        if i_a < 0:
                            i_a = len(arrow_pos) - 1
                        pygame.time.delay(30)

            self.screen.fill((0, 0, 0))
            self.screen.blit(menu_surface, (0, 0))
            self.screen.blit(arrow, arrow_pos[i_a])
            pygame.display.flip()
        return 'QUIT'

    def option(self) -> str:
        """
        Отвечает за прорисовку настроек во время игры
        (Включается при нажатии ESC в игре, кроме битвы).
        :return: Строка следующего состояния
        """
        check_pos = [(835, 242),
                     (835, 285)]
        check = self.icon['check']
        arrow = self.icon['arrow_right']
        arrow_pos = [(560, 233),
                     (560, 279),
                     (560, 320),
                     (560, 362),
                     (560, 404),
                     (560, 448)]
        i_a = 0
        donne = True
        while donne and self.RUN:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.RUN = False
                    return 'QUIT'
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        donne = False
                    elif e.key == pygame.K_RETURN:
                        if i_a == 0:
                            # Окно сообщений
                            self.show_message_frame = not self.show_message_frame
                        elif i_a == 1:
                            # Свечение
                            self.show_glow = not self.show_glow
                        elif i_a == 2:
                            # Сохранить
                            com = self.save()
                            if com != 'OK':
                                return com
                        elif i_a == 3:
                            # Загрузить
                            return 'LOAD'
                        elif i_a == 4:
                            # Титры
                            pass
                        elif i_a == 5:
                            # Выход
                            self.RUN = False
                            return 'QUIT'

                    elif e.key == pygame.K_DOWN:
                        i_a += 1
                        if i_a >= len(arrow_pos):
                            i_a = 0
                        pygame.time.delay(30)
                    elif e.key == pygame.K_UP:
                        i_a -= 1
                        if i_a < 0:
                            i_a = len(arrow_pos) - 1
                        pygame.time.delay(30)
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.option_frame, (0, 0))
            if self.show_message_frame:
                self.screen.blit(check, check_pos[0])
            if self.show_glow:
                self.screen.blit(check, check_pos[1])
            self.screen.blit(arrow, arrow_pos[i_a])
            pygame.display.flip()
        return 'OK'

    def check_obj(self, terra: Map) -> str:
        """
        Проверяет объекты на карте.
        Gate-вход куда либо.
        Exit-выход из помещения.
        :param terra: Текущая карта
        :return: Строка следующего состояния
        """
        if not terra.obj:
            return 'OK'

        x = self.current_player.pos_x + self.current_player.center_x_const
        y = self.current_player.pos_y + self.current_player.center_y_const
        for obj in terra.obj.objects:
            if obj.x < x < obj.x + obj.width and obj.y < y < obj.y + obj.height:
                if obj.type == "Gate":
                    name = obj.properties["path"]
                    self.current_player.pos_x = int(obj.properties["pos_x"])
                    self.current_player.pos_y = int(obj.properties["pos_y"])
                    self.current_map = PATH_TO_MAP + name
                    return 'JUMP'
                if obj.type == 'Spawn':
                    if random.randint(0, int(obj.properties["random"])) == 1:
                        return self.battle()
        return 'OK'

    def map_run(self, terra: Map) -> str:
        """
        Основной игровой цикл на карте.
        :param terra: Текущая карта
        :return: Строка следующего состояния
        """
        k = 0
        terra.start_pos_hero(self.current_player)
        clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT + 0, 1000)
        pygame.time.set_timer(pygame.USEREVENT + 1, DELAY_SEND)
        old_running = running = False

        dial_flag = False
        msg_input = Game.new_msg()
        direction_x = direction_y = 0
        terra.done = True
        while terra.done and self.RUN:
            dt = clock.tick(FPS)
            # event handing
            events = pygame.event.get()
            if dial_flag:
                if msg_input.update(events):
                    msg = msg_input.get_text()
                    if self.run_tcp:
                        self.sock_tcp.send(self.current_player.encode_tcp(0, msg))
                    self.message_frame.add(self.current_player.login.decode(), msg)
                    dial_flag = False
                    msg_input = Game.new_msg()

            for event in events:
                if event.type == pygame.QUIT:
                    self.RUN = False
                    return 'QUIT'
                elif event.type == pygame.USEREVENT + 0:
                    pass
                    # print("FPS: ", clock.get_fps())
                elif event.type == pygame.USEREVENT + 1 and self.run_udp:
                    self.sock_udp.sendto(self.current_player.encode_udp(running), (HOST, PORT_UDP))

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        com = self.option()
                        if com != 'OK':
                            terra.done = False
                            return com
                    elif event.key == pygame.K_p and not dial_flag:
                        pass
                        # self.num_player += 1
                        # self.num_player = self.num_player if self.num_player < 4 else 0
                        # self.current_player.update_anim(self.players[self.num_player])
                        # if self.run_tcp:
                        #     self.sock_tcp.send(self.current_player.encode_tcp(4))
                        # pygame.time.delay(400)
                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        running = True
                    elif event.key == pygame.K_q:
                        dial_flag = True
                    elif event.key == pygame.K_b:
                        pass
                        # com = self.battle()
                        # if com != 'OK':
                        #     return com

                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        running = False

            if running:
                rate = self.current_player.run_rate
            else:
                rate = self.current_player.walk_rate

            if dial_flag:
                self.current_player.direction_x = 0
                self.current_player.direction_y = 0
            else:
                self.current_player.direction_x = pygame.key.get_pressed()[pygame.K_RIGHT] - \
                                                  pygame.key.get_pressed()[pygame.K_LEFT]
                self.current_player.direction_y = pygame.key.get_pressed()[pygame.K_DOWN] - \
                                                  pygame.key.get_pressed()[pygame.K_UP]

            if self.current_player.direction_y == 1:
                self.current_player.direction = 0
            elif self.current_player.direction_y == -1:
                self.current_player.direction = 3
            if self.current_player.direction_x == 1:
                self.current_player.direction = 2
            elif self.current_player.direction_x == -1:
                self.current_player.direction = 1

            dir_len = math.hypot(self.current_player.direction_x, self.current_player.direction_y)
            dir_len = dir_len if dir_len else 1.0
            # update position
            dx = rate * dt * self.current_player.direction_x / dir_len
            dy = rate * dt * self.current_player.direction_y / dir_len
            dx, dy = terra.check_collision(self.current_player, dx, dy)
            dx, dy = terra.check_wall(self.current_player, dx, dy)

            if self.run_udp:
                if self.current_player.direction_x != direction_x:
                    self.sock_udp.sendto(self.current_player.encode_udp(running), (HOST, PORT_UDP))
                    direction_x = self.current_player.direction_x
                    direction_y = self.current_player.direction_y
                    old_running = running
                elif self.current_player.direction_y != direction_y:
                    self.sock_udp.sendto(self.current_player.encode_udp(running), (HOST, PORT_UDP))
                    direction_x = self.current_player.direction_x
                    direction_y = self.current_player.direction_y
                    old_running = running
                elif running != old_running:
                    self.sock_udp.sendto(self.current_player.encode_udp(running), (HOST, PORT_UDP))
                    direction_x = self.current_player.direction_x
                    direction_y = self.current_player.direction_y
                    old_running = running

            com = self.check_obj(terra)
            if com != 'OK':
                return com

            self.screen.fill((0, 0, 0))
            i = 0
            for layer in terra.layers:
                terra.renderer.render_layer(self.screen, layer)
                if i == terra.layer_player:
                    if self.current_player.level != 0:
                        for friend in self.friends.values():
                            if friend.level == self.current_player.level:
                                if friend.direction_x or friend.direction_y:
                                    friend.move(friend.rate * dt * friend.direction_x / friend.dir_len,
                                                friend.rate * dt * friend.direction_y / friend.dir_len)
                                    friend.move_conductor.play()
                                    friend.anim_objs[friend.direction].blit(self.screen,
                                                                            friend.cord(self.current_player))
                                else:
                                    friend.move_conductor.stop()
                                    self.screen.blit(friend.standing[friend.direction],
                                                     friend.cord(self.current_player))

                    if self.current_player.direction_x or self.current_player.direction_y:
                        self.current_player.move_conductor.play()
                        self.current_player.move(dx, dy)
                        self.current_player.anim_objs[self.current_player.direction].blit(self.screen, (CEN_X, CEN_Y))
                    else:
                        self.current_player.move_conductor.stop()
                        self.screen.blit(self.current_player.standing[self.current_player.direction], (CEN_X, CEN_Y))
                i += 1
            terra.renderer.set_camera_position(*self.current_player.get_pos_cam())

            if dial_flag:
                self.screen.blit(self.dial_frame, (0, 642))
                self.screen.blit(self.current_player.face[0], (32, 657))
                self.screen.blit(msg_input.get_surface(), (128, 697))

            if self.show_message_frame:
                self.screen.blit(self.message_frame.get_surface(), (WIDTH * 3 // 4, 0))
            if self.show_glow:
                self.screen.blit(self.icon['glow'], (CEN_X, CEN_Y))

            pygame.display.flip()
        return 'OK'

    @staticmethod
    def pygame_init() -> pygame.Surface:
        """
        Статический метод для создания основного окна и инициализации Pygame
        :return: Основное окно
        """
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('RPG')
        screen_width = WIDTH
        screen_height = HEIGHT
        return pygame.display.set_mode((screen_width, screen_height))

    @staticmethod
    def icon_init() -> dict:
        """
        Статический метод для создания словаря мелких изображений.
        :return: Словарь изображений по названию
        """
        paths = list(filter(os.path.isfile, map(lambda x: 'IMG/Icon/' + x, os.listdir('IMG/Icon'))))
        keys = list(map(lambda x: x[9:-4], paths))
        items = list(zip(keys, list(map(lambda x: pygame.image.load(x), paths))))
        return dict(items)

    @staticmethod
    def settings_init() -> dict:
        """
        Статический метод для создания словаря "флагов".
        :return: Словарь флагов по названию
        """
        return {
            'message_frame': True,
            'glow': False,
        }

    @staticmethod
    def new_msg(color=(255, 255, 255), font_size=18, max_len=64) -> pygame_textinput.TextInput:
        """
        Статический метод возвращающий новую строку ввода.
        :return: Новая строка ввода
        """
        return pygame_textinput.TextInput(font_family='Font/UbuntuMono-R.ttf',
                                          font_size=font_size,
                                          antialias=True,
                                          text_color=color,
                                          cursor_color=color,
                                          max_len=max_len)

    def listen_udp(self):
        """
        Цикл пролушки UDP соединения
        :return: None
        """
        self.run_udp = True
        while self.run_udp and self.RUN:
            try:
                data, _ = self.sock_udp.recvfrom(1024)
            except socket.timeout:
                continue
            except ConnectionResetError:
                break
            if not data:
                continue
            Friend.decode_udp(data, self.friends)

    def listen_tcp(self):
        """
        Цикл прослушки TCP соединения
        :return: None
        """
        self.run_tcp = True
        self.sock_tcp.send(self.current_player.encode_tcp(1))
        while self.run_tcp and self.RUN:
            try:
                data = self.sock_tcp.recv(1024)
            except socket.timeout:
                continue
            if not data:
                continue
            Friend.decode_tcp(data, self.friends, self.message_frame)

    def start(self) -> str:
        """
        Запуск всей игры.
        :return: Строка следущего состояния
        """
        if not (self.run_tcp and self.sock_udp):
            self.connect()
        listen_udp = threading.Thread(target=self.listen_udp, args=())
        listen_tcp = threading.Thread(target=self.listen_tcp, args=())
        if self.online:
            listen_udp.start()
            listen_tcp.start()

        com = 'JUMP'
        while com == 'JUMP':
            com = self.map_run(Map(self.current_map))

        if self.online:
            self.sock_udp.sendto(b'', (HOST, PORT_UDP))
            self.sock_tcp.send(self.current_player.encode_tcp(2))
            listen_tcp.join()
            self.sock_tcp.close()
            listen_udp.join()
            self.sock_udp.close()

        return com

    def check_login(self, login: str) -> bool:
        """
        Проверка логина
        :param login: Сам логин
        :return: Можно использовать или нет
        """
        d = len(login).to_bytes(length=1, byteorder='big', signed=False)
        log = bytes(login, encoding='utf-8')
        label = (3).to_bytes(length=1, byteorder='big', signed=False)
        self.sock_tcp.send(d+log+label)
        data = self.sock_tcp.recv(1024)
        if len(data) == 0:
            print('ERROR')
            return False
        else:
            return bool(int(data[0]))

    def new_authorization(self) -> str:
        """
        Страница авторизации, для нового игрока
        :return: Строка следущего состояния
        """
        try:
            os.mkdir('Save')
        except OSError:
            pass
        try:
            with open('Save/login', 'r') as f:
                login = f.read(255)
                if len(login) >= 3:
                    self.login = login
                    return 'OK'
        except FileNotFoundError:
            pass
        auth_surface = pygame.image.load('IMG/Frames/Authorization.png')
        err = pygame.image.load('IMG/Other/Message.png')
        err_log = pygame.image.load('IMG/Other/Error_login.png')
        show_err = False
        show_err_log = False
        arrow = pygame.transform.scale(self.icon['arrow_left'], (16, 16))
        arrow_pos = [(970, 464), (970, 495), (970, 527)]
        msg_input = self.new_msg((0, 0, 0), 18, 18)
        i_a = 0
        while self.RUN:
            events = pygame.event.get()
            msg_input.update(events)
            for event in events:
                if event.type == pygame.QUIT:
                    self.RUN = False
                    return 'QUIT'
                elif event.type == pygame.KEYDOWN:
                    show_err = False
                    show_err_log = False
                    if event.key == pygame.K_RETURN:
                        if i_a == 0:
                            login = msg_input.get_text()
                            if len(login) >= 3:
                                if not self.online:
                                    self.online = True
                                    self.connect()
                                if self.check_login(login):
                                    with open('Save/login', 'w') as f:
                                        f.write(login)
                                    self.login = msg_input.get_text()
                                    return 'OK'
                                else:
                                    show_err_log = True
                                    msg_input = self.new_msg((0, 0, 0), 18, 18)
                            else:
                                show_err = True
                        elif i_a == 1:
                            self.online = False
                            return 'OK'
                        elif i_a == 2:
                            self.RUN = False
                            return 'QUIT'
                    elif event.key == pygame.K_DOWN:
                        i_a += 1
                        if i_a >= len(arrow_pos):
                            i_a = 0
                        pygame.time.delay(30)
                    elif event.key == pygame.K_UP:
                        i_a -= 1
                        if i_a < 0:
                            i_a = len(arrow_pos) - 1
                        pygame.time.delay(30)

            self.screen.fill((0, 0, 0))
            self.screen.blit(auth_surface, (0, 0))
            self.screen.blit(msg_input.get_surface(), (785, 413))
            self.screen.blit(arrow, arrow_pos[i_a])
            if show_err:
                self.screen.blit(err, (785, 575))
            if show_err_log:
                self.screen.blit(err_log, (813, 575))
            pygame.display.flip()
        return 'QUIT'

    def view_logo(self):
        """
        Показ логотипа на 2 секунды
        :return: None
        """
        logo = pygame.image.load('IMG/Other/logo.png')
        self.screen.fill((255, 255, 255))
        self.screen.blit(logo, (265, 196))
        pygame.display.flip()
        pygame.time.wait(2000)

    @staticmethod
    def init_hero(key: str) -> Hero:
        """
        Инициация героя без имени
        :param key: ID героя, тот же что и в Life
        :return: Hero
        """
        args = Life.database.init_hero(key)
        return Hero('', *args[0:3],
                    at_list=(
                        Attack(name='mag_atk', size=args[3], cost=args[4], atr_type='mp', defense='mag_def'),
                        Attack(name='ph_atk', size=args[5], cost=args[6], atr_type='sp', defense='ph_def')
                    ),
                    df_list=(
                        Defence(name='fire_def', size=args[7]),
                        Defence(name='ph_def', size=args[8])
                    ))

    def init_person(self) -> str:
        """
        Окно создания пероснажей
        :return: Строка следующего состояния
        """
        flag_duplicate = 0
        msg_dup = pygame.image.load('IMG/Other/Message1.png')
        cord_x_dup = 50
        flag_nil = 0
        msg_nil = pygame.image.load('IMG/Other/Message2.png')
        cord_x_nil = 39
        cord_y_msg = [460, 490]
        msg_random_character = pygame.image.load('IMG/Other/Random_character.png')

        key = ['noname',
               'actor100', 'actor101', 'actor102', 'actor103', 'actor104', 'actor105', 'actor106', 'actor107',
               'actor200', 'actor201', 'actor202', 'actor203', 'actor204', 'actor205', 'actor206', 'actor207',
               'actor300', 'actor301', 'actor302', 'actor303', 'actor304', 'actor305', 'actor306', 'actor307']
        anim = list(map(lambda x: Life(x), key))
        hero = list(map(lambda x: Game.init_hero(x), key))
        names = []

        init_surface = pygame.image.load('IMG/Frames/init.png')
        # card_surface = pygame.image.load('IMG/Frames/....py')

        name_input = self.new_msg((0, 0, 0), 18, 11)
        font_object = pygame.font.Font('Font/UbuntuMono-R.ttf', 20)

        arrow = pygame.transform.scale(self.icon['arrow_left'], (16, 16))
        arrow_pos = [(165, 543 + x * 29) for x in range(3)]

        i_a = 0
        ind = 0
        while self.RUN:
            events = pygame.event.get()
            name_input.update(events)
            for event in events:
                if event.type == pygame.QUIT:
                    self.RUN = False
                    return 'QUIT'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if i_a == 0:
                            # Продолжить
                            name = name_input.get_text()
                            if len(name) == 0:
                                flag_nil = flag_duplicate + 1 if not flag_nil else flag_nil
                            elif name in names:
                                flag_duplicate = flag_nil + 1 if not flag_duplicate else flag_duplicate
                            else:
                                if ind == 0:
                                    ind = random.randint(1, len(key) - 1)
                                names.append(name)
                                hero[ind].name = name
                                self.heroes.append(hero[ind])
                                self.players.append(anim[ind])
                                if len(names) == 4:
                                    self.current_player = Player(self.login, self.players[0].key)
                                    return 'OK'
                                key.pop(ind)
                                anim.pop(ind)
                                hero.pop(ind)
                                name_input = self.new_msg((0, 0, 0), 18, 11)
                                flag_duplicate = 0
                                flag_nil = 0
                                ind = 0
                        elif i_a == 1:
                            # Меню
                            return 'MENU'
                        elif i_a == 2:
                            # Выход
                            self.RUN = False
                            return 'QUIT'
                    elif event.key == pygame.K_RIGHT:
                        ind += 1
                        if ind >= len(key):
                            ind = 0
                        pygame.time.delay(30)
                    elif event.key == pygame.K_LEFT:
                        ind -= 1
                        if ind < 0:
                            ind = len(key) - 1
                        pygame.time.delay(30)
                    elif event.key == pygame.K_DOWN:
                        i_a += 1
                        if i_a >= len(arrow_pos):
                            i_a = 0
                        pygame.time.delay(30)
                    elif event.key == pygame.K_UP:
                        i_a -= 1
                        if i_a < 0:
                            i_a = len(arrow_pos) - 1
                        pygame.time.delay(30)
            self.screen.fill((0, 0, 0))
            self.screen.blit(init_surface, (0, 0))
            self.screen.blit(arrow, arrow_pos[i_a])
            self.screen.blit(anim[ind].face[0], (32, 32))
            anim[ind].move_conductor.play()
            anim[ind].anim_objs[1].blit(self.screen, (185, 64))
            anim[ind].anim_objs[3].blit(self.screen, (217, 32))
            self.screen.blit(anim[ind].standing[0], (217, 64))
            anim[ind].anim_objs[0].blit(self.screen, (217, 96))
            anim[ind].anim_objs[2].blit(self.screen, (249, 64))
            if flag_nil:
                self.screen.blit(msg_nil, (cord_x_nil, cord_y_msg[flag_nil - 1]))
            if flag_duplicate:
                self.screen.blit(msg_dup, (cord_x_dup, cord_y_msg[flag_duplicate - 1]))
            if ind == 0:
                self.screen.blit(msg_random_character, (76, 140))
            self.screen.blit(name_input.get_surface(), (173, 173))
            # HP
            self.screen.blit(font_object.render('{0}/{0}'.format(hero[ind].hp), True, (0, 0, 0)), (171, 210))
            # MP
            self.screen.blit(font_object.render('{0}/{0}'.format(hero[ind].mp), True, (0, 0, 0)), (171, 245))
            # SP
            self.screen.blit(font_object.render('{0}/{0}'.format(hero[ind].sp), True, (0, 0, 0)), (171, 280))
            # Ph_atk
            self.screen.blit(
                font_object.render('{0}'.format(hero[ind].at_list[1].size), True, (0, 0, 0)),
                (171, 315)
            )
            # Mag_atk
            self.screen.blit(
                font_object.render('{0}'.format(hero[ind].at_list[0].size), True, (0, 0, 0)),
                (171, 349)
            )
            # Ph_def
            self.screen.blit(
                font_object.render('{0}'.format(hero[ind].df_list[1].size), True, (0, 0, 0)),
                (171, 384)
            )
            # Mag_def
            self.screen.blit(
                font_object.render('{0}'.format(hero[ind].df_list[0].size), True, (0, 0, 0)),
                (171, 419)
            )
            pygame.display.flip()
        return 'QUIT'

    def game_over(self):
        """
        Показ окончания игры
        :return: None
        """
        frame = pygame.image.load('IMG/Frames/game_over.jpg')
        self.screen.fill((0, 0, 0))
        self.screen.blit(frame, (0, 0))
        pygame.display.flip()
        pygame.time.wait(2000)

    def battle(self) -> str:
        """
        Цикл битвы
        :return:
        """
        self.players[0].pos_x, self.players[0].pos_y = 700, 400
        self.players[1].pos_x, self.players[1].pos_y = 750, 450
        self.players[2].pos_x, self.players[2].pos_y = 800, 500
        self.players[3].pos_x, self.players[3].pos_y = 850, 550

        heroes = (self.heroes, self.players)
        enemies = create_enemies()
        local_player = HelpClass(self.heroes)
        scene = BattleScene(self.screen, 'Battle/images/bg.png', heroes, enemies)
        scene.render()
        pygame.display.update()
        while self.RUN:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.RUN = False
                    return 'QUIT'

            result = choice(scene)
            animation(scene, result, local_player)
            reset(scene, 3)
            if not check_life(heroes[0]):
                # Game Over
                self.game_over()
                return 'MENU'
            if not check_life(enemies[0]):
                # You Win
                self.search_life_hero()
                return 'OK'
        return 'QUIT'


def start_game():
    os.chdir(os.path.dirname(__file__))
    g = Game()
    g.RUN = True
    g.view_logo()
    com = g.new_authorization()
    if com == 'OK':
        com = g.menu()
    while com != 'QUIT':
        if com == 'NEW':
            com = g.init_person()
            if com == 'OK':
                com = g.start()
        elif com == 'MENU':
            com = g.menu()
        elif com == 'LOAD':
            com = g.load()
            if com == 'OK':
                com = g.start()
    pygame.font.quit()
    pygame.quit()


def test():
    os.chdir(os.path.dirname(__file__))
    g = Game()
    g.RUN = True
    g.login = str(int(time.time()) % 100)
    g.view_logo()
    com = 'OK'
    g.online = True
    if com == 'OK':
        com = g.menu()
    while com != 'QUIT':
        if com == 'NEW':
            com = g.init_person()
            if com == 'OK':
                com = g.start()
        elif com == 'MENU':
            com = g.menu()
        elif com == 'LOAD':
            com = g.load()
            if com == 'OK':
                com = g.start()
    pygame.font.quit()
    pygame.quit()


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

'''
QUIT
MENU
LOAD
NEW
OK
'''

if __name__ == "__main__":
    start_game()
