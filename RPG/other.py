import pygame
import textwrap
import os

__all__ = ['Message',
           'FPS', 'DELAY_SEND',
           'WIDTH', 'HEIGHT', 'CEN_X', 'CEN_Y',
           'PATH_TO_MAP', 'PATH_TO_LOG',
           'HOST', 'PORT_UDP', 'PORT_TCP']

FPS = 0
DELAY_SEND = 1000

WIDTH = 1024
HEIGHT = 768
CEN_X = WIDTH // 2 - 16
CEN_Y = HEIGHT // 2 - 16

PATH_TO_MAP = 'TilesMap/'
PATH_TO_LOG = 'game.log'

# HOST = "188.226.185.13"
HOST = "0.0.0.0"
PORT_UDP = 17070
PORT_TCP = 17071


class Message:
    """
    Класс для рамки сообщений
    """

    def __init__(self, font_path: str, font_size: int, frame: str, w=WIDTH // 4, h=HEIGHT):
        """
        :param font_path: Путь к шрифту
        :param font_size: Размер текста
        :param frame: Путь к изображению рамки
        :param w: Длина рамки
        :param h: Высота рамки
        """
        self.colors = []
        self.strings = []
        if not os.path.isfile(font_path):
            font_path = pygame.font.match_font(font_path)
        self.font_object = pygame.font.Font(font_path, font_size)
        self.frame = pygame.transform.scale(pygame.image.load(frame), (w, h))
        self.surface = self.frame.copy()
        self.w = w
        self.wch = (w - 40) // self.font_object.size('a')[0]
        self.h = h
        self.hch = (h - 40) // self.font_object.size('a')[1]

    @staticmethod
    def login_to_rgb(login: str) -> (int, int, int):
        """
        Функция возвращает цвет для логина
        У каждого пользователя свой цвет сообщения
        :param login: Логин игрока
        :return: Цвет в RGB
        """
        h = hash(login)
        r = (h & 0xFF0000) >> 16
        g = (h & 0x00FF00) >> 8
        b = (h & 0x0000FF)
        return r, g, b

    def add(self, login: str, msg: str):
        """
        Метод добавления соощения в класс
        :param login: логин пользователя
        :param msg: тест сообщения
        :return: None
        """
        msg = textwrap.fill('{0}> {1}\n'.format(login, msg), self.wch)
        lines = msg.split('\n')
        self.colors += [(Message.login_to_rgb(login))] * len(lines)
        self.strings += lines
        self.render_lines()

    def render_lines(self):
        """
        Обновляет Surface
        :return: None
        """
        self.surface = self.frame.copy()
        up = -self.font_object.get_height() + 20
        down = self.surface.get_height() - self.font_object.get_height() - 20
        dy = -self.font_object.get_height()
        i = -1
        for y in range(down, up, dy):
            if i < -len(self.strings):
                break
            else:
                self.surface.blit(
                    self.font_object.render(self.strings[i], True, self.colors[i]),
                    (20, y))
            i -= 1

    def get_surface(self) -> pygame.Surface:
        """
        Возвращает рамку
        :return: Рамка
        """
        return self.surface
