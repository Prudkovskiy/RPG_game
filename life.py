import logging
import math
import os

import pygame
import pyganim

import sql
from other import *

__all__ = ['Life', 'Player', 'Friend',
           'SPECIAL_ID']

SPECIAL_ID = ['asuka',
              'katsuragi',
              'shinji',
              'noname']


class Life:
    """
    Класс Life - базовый класс для всех живых объектов:
    Player;
    Friend;
    NPC; (Пока в разарботке)
    """
    database = sql.DB()

    def __init__(self, key: str):
        """
        Инициализет анимацию объекта
        :param key: ID анимации в базе данных
        """
        try:
            img, width, height, num, st, x, y = Life.database.init_life(key)
        except ValueError:
            logging.error("ID=%s not found" % (key,))
            return
        self.img_width = width
        self.img_height = height

        self.anim_objs = [None] * 4
        self.standing = [None] * 4
        # 0-front, 1-left, 2-right, 3-back
        for i in range(4):
            rects = [(x + num * width, y + i * height, width, height) for num in range(num)]
            all_images = pyganim.getImagesFromSpriteSheet(img, rects=rects)
            all_images = list(map(lambda a: a.convert_alpha(), all_images))
            self.standing[i] = all_images[st]
            frames = list(zip(all_images, [120] * len(all_images)))
            self.anim_objs[i] = pyganim.PygAnimation(frames)
        self.move_conductor = pyganim.PygConductor(self.anim_objs)

        self.pos_x = -1
        self.pos_y = -1

        self.run_rate = 0.45
        self.walk_rate = 0.15

        self.key = key

        self.direction = 0
        self.direction_x = 0
        self.direction_y = 0
        self.level = -1
        self.face = self.load_face()

    def load_face(self) -> list:
        """
        Загружает изображения лиц персонажа
        :return: Список лиц
        """
        if self.key in SPECIAL_ID:
            files = list(map(lambda x: 'IMG/Hero/Face/' + self.key + '/' + x, os.listdir('IMG/Hero/Face/' + self.key)))
            files = list(filter(os.path.isfile, files))
            return list(map(lambda x: pygame.image.load(x), files))
        else:
            n = int(self.key[-2:])
            path = 'IMG/Hero/Face/' + self.key[:-2] + '.png'
            rect = ((n % 4) * 96, (n // 4) * 96, 96, 96)
            return list(pyganim.getImagesFromSpriteSheet(path, rects=[rect]))

    def move(self, dx, dy):
        """
        Метод обновления координат
        :param dx: Дельта X
        :param dy: Дельта Y
        :return: None
        """
        self.pos_x += dx
        self.pos_y += dy

    def get_pos(self):
        """
        Возвращает позицию объекта
        :return: Позиция объекта
        """
        return self.pos_x, self.pos_y

    def update_anim(self, other):
        """
        Обновление анимации у героя
        :param other: Объект Life с новой анимацией
        :return: None
        """
        self.standing = other.standing
        self.anim_objs = other.anim_objs
        self.move_conductor = other.move_conductor
        self.key = other.key
        self.face = other.face


class Player(Life):
    """
    Класс основного игрока
    """
    def __init__(self, login: str, key: str, rect_coll=(16, 0, 2, 2)):
        """
        :param login: Логин игрока
        :param key: ID анимации в базе данных
        :param rect_coll: Отступ сверху, снизу, слева и справа соответсвенно. Для обработки столкновений
        """
        super().__init__(key)

        self.UP = rect_coll[0]
        self.DOWN = self.img_height - rect_coll[1]
        self.LEFT = rect_coll[2]
        self.RIGHT = self.img_width - rect_coll[3]

        self.center_x_const = self.LEFT + (self.RIGHT - self.LEFT) // 2
        self.center_y_const = self.UP + (self.DOWN - self.UP) // 2

        self.d = len(login).to_bytes(length=1, byteorder='big', signed=False)
        self.login = bytes(login, encoding='utf-8')

        self.stack = []

    def get_pos_cam(self):
        """
        Возвращает позицию для камеры
        :return: Позиция камеры
        """
        return self.pos_x + 16, self.pos_y + 16

    def help_func(self, dx, dy) -> (float, float, float, float):
        """
        Вспомогательная функция для обработки столкновений
        :param dx: Дельта X
        :param dy: Дельта Y
        :return: X слева, справа, Y сверху, снизу
        """
        left = self.pos_x + dx + self.LEFT
        right = self.pos_x + dx + self.RIGHT
        up = self.pos_y + dy + self.UP
        down = self.pos_y + dy + self.DOWN
        return left, right, up, down

    def push(self, x, y, map):
        """
        Добовляет в стек информацию
        Срабатывает при входе в помещение
        :param x: Позиция X
        :param y: Позиция Y
        :return: None
        """
        self.stack.append((x, y, self.level, map))

    def pop(self):
        """
        Обновляет координаты из стека.
        Срабатывает при выходе из помещения
        :return: None
        """
        self.pos_x, self.pos_y, self.level, map = self.stack.pop()
        return map

    def encode_udp(self, running: bool) -> bytes:
        """
        Кодирует позицию игрока для отпраки
        :param running: Флаг, который указывает на бег
        :return: Байты для отправки
        """
        x = round(self.pos_x).to_bytes(length=4, byteorder='big', signed=False)
        y = round(self.pos_y).to_bytes(length=4, byteorder='big', signed=False)
        direct = ((self.direction_x + 1) * 3 + self.direction_y + 1).to_bytes(length=1, byteorder='big', signed=False)
        flag = (running * 4 + self.direction).to_bytes(length=1, byteorder='big', signed=False)
        level = self.level.to_bytes(length=1, byteorder='big', signed=False)
        return self.d + self.login + x + y + direct + flag + level

    def encode_tcp(self, label: int, msg='') -> bytes:
        """
        Кодирует сообщение в байты для отправки.
        :param msg: Само сообщение
        :param label: Указывает на тип сообщения
                0 - пишет соощение в Message
                1 - добовляет нового игрока
                2 - удаляет игрока из списка
                3 - отправляет запрос на проверку логина
                4 - сообщение о смене внешности
        :return: Байты для отправки
        """
        flag = label.to_bytes(length=1, byteorder='big', signed=False)
        if label == 0:
            # Отпрака нового сообщения
            message = bytes(msg, encoding='utf-8')
            return self.d + self.login + flag + message
        elif label in (1, 4):
            # Сообщение о присоединении к игре
            # Сообщение о смене внешности
            key = bytes(self.key, encoding='utf-8')
            return self.d + self.login + flag + key
        elif label in (2, 3):
            # Сообщение о выходе игрока
            # Сообщение о проверки логина
            return self.d + self.login + flag


class Friend(Life):
    """
    Класс других игроков.
    """
    def __init__(self, key: str, login: bytes,):
        """
        :param key: ID анимации в базе данных
        :param login: Логин игрока в байтовой строке
        """
        super().__init__(key)
        self.login = login
        self.stop = True
        self.dir_len = 1
        self.rate = self.walk_rate

    def cord(self, player: Player):
        """
        Возвращает координаты относительно основного игрока
        :param player: Ссылка на онсовного игрока
        :return: Координата в X и Y
        """
        return CEN_X - (player.pos_x - self.pos_x), CEN_Y - (player.pos_y - self.pos_y)

    def update(self, data: bytes):
        """
        Обновление позиции, по пришедшему сообщению.
        :param data: Байты с информацией
        :return: None
        """
        self.pos_x = int.from_bytes(bytes=data[0:4], byteorder='big', signed=False)
        self.pos_y = int.from_bytes(bytes=data[4:8], byteorder='big', signed=False)
        direct = int(data[8])
        self.direction_x = direct // 3 - 1
        self.direction_y = direct % 3 - 1
        flag = int(data[9])
        self.direction = flag % 4
        self.rate = self.run_rate if flag // 4 else self.walk_rate
        self.level = int.from_bytes(bytes=data[10:11], byteorder='big', signed=False)

        self.dir_len = math.hypot(self.direction_x, self.direction_y)
        self.dir_len = self.dir_len if self.dir_len else 1.0

    @staticmethod
    def decode_udp(data: bytes, dic: dict):
        """
        Декодирует пришедшее по UDP сообщение
        Ищет в словаре игрока с таким же логином и обновляет для него координтаы
        :param data: Пришедщее сообщение
        :param dic: Словарь с игроками по логину
        :return: None
        """
        d = int(data[0])
        login = data[1:d + 1]
        fr = dic.get(login, None)
        if fr is not None:
            fr.update(data[d + 1:])

    @staticmethod
    def decode_tcp(data: bytes, dic: dict, mf: Message):
        """
        Декодирует пришедшее по TCP сообщение
        Смотрит на метку и выполняет соответвующую операцию:
        0 - пишет соощение в Message
        1 - добовляет нового игрока
        2 - удаляет игрока из списка
        3 - отправляет запрос на проверку логина
        4 - сообщение о смене внешности
        :param data: Пришедшее сообщение
        :param dic: Словарь с игроками по логину
        :param mf: Рамка с сообщениями
        :return: None
        """
        d = int(data[0])
        login = data[1:d + 1]
        label = int(data[d + 1])
        data = data[d + 2:]
        if label == 0:
            mf.add(login.decode(), data.decode())
        elif label == 1:
            dic[login] = Friend(data.decode(), login)
        elif label == 2:
            try:
                del dic[login]
            except KeyError:
                logging.error("Key=%s not found" % (login,))
        elif label == 3:
            pass
        elif label == 4:
            try:
                dic[login].update_anim(Life(data.decode()))
            except KeyError:
                logging.error("Key=%s not found" % (login,))
