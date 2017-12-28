from RPG import tiledtmxloader
from RPG.life import *
from RPG.other import *

__all__ = ['Map']


class Map:
    """
    Класс работаюзий с картами
    """
    def __init__(self, file_name: str):
        """
        :param file_name: Путь к карте
        """
        world_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(file_name)
        self.resources = tiledtmxloader.helperspygame.ResourceLoaderPygame()
        self.resources.load(world_map)

        assert world_map.orientation == "orthogonal"
        self.layer_player = int(world_map.properties["layer_player"])
        n_coll = int(world_map.properties["layer_coll"])
        self.start_x = int(world_map.properties["start_x"])
        self.start_y = int(world_map.properties["start_y"])
        self.level = int(world_map.properties["level"])
        self.flag = world_map.properties["flag"] == "true"

        self.tile_width = world_map.tilewidth
        self.tile_height = world_map.tileheight

        self.renderer = tiledtmxloader.helperspygame.RendererPygame()

        if self.flag:
            cam_pos_x = int(world_map.properties["cam_pos_x"]) * world_map.tilewidth + world_map.tilewidth // 2
            cam_pos_y = int(world_map.properties["cam_pos_y"]) * world_map.tileheight + world_map.tileheight // 2
            cam_size_x = int(world_map.properties["cam_size_x"]) * world_map.tilewidth
            cam_size_y = int(world_map.properties["cam_size_y"]) * world_map.tileheight
        else:
            cam_pos_x = self.start_x * world_map.tilewidth + world_map.tilewidth // 2
            cam_pos_y = self.start_y * world_map.tileheight + world_map.tileheight // 2
            cam_size_x = WIDTH
            cam_size_y = HEIGHT

        self.renderer.set_camera_position_and_size(cam_pos_x, cam_pos_y, cam_size_x, cam_size_y)

        obj_layers = []
        self.layers = []
        for layer in tiledtmxloader.helperspygame.get_layers_from_map(self.resources):
            if layer.is_object_group:
                obj_layers.append(layer)
            else:
                self.layers.append(layer)
        self.obj = None
        self.wall = None
        for layer in obj_layers:
            if layer.name == "Wall":
                self.wall = layer
            elif layer.name == "Obj":
                self.obj = layer

        self.collision = self.layers.pop(n_coll)
        self.done = False

    def check_collision(self, player: Player, dx: float, dy: float) -> (float, float):
        """
        Провряет столкновение
        :param player: Основной игрок
        :param dx: Дельта X
        :param dy: Дельта Y
        :return: Обновленные dx, dy
        """
        if dx >= 32 or dy >= 32:
            return 0, 0

        left, right, up, down = map(lambda x: int(x) // 32, player.help_func(dx, 0))
        if dx > 0:
            if self.collision.content2D[up][right] is not None or \
                            self.collision.content2D[down][right] is not None:
                dx = 0
                player.pos_x = right * 32 - player.RIGHT - 0.5
                player.direction_x = 0
        elif dx < 0:
            if self.collision.content2D[up][left] is not None or \
                            self.collision.content2D[down][left] is not None:
                dx = 0
                player.pos_x = (left + 1) * 32 - player.LEFT + 0
                player.direction_x = 0

        left, right, up, down = map(lambda x: int(x) // 32, player.help_func(0, dy))
        if dy > 0:
            if self.collision.content2D[down][left] is not None or \
                            self.collision.content2D[down][right] is not None:
                dy = 0
                player.pos_y = down * 32 - player.DOWN - 0.5
                player.direction_y = 0
        elif dy < 0:
            if self.collision.content2D[up][left] is not None or \
                            self.collision.content2D[up][right] is not None:
                dy = 0
                player.pos_y = (up + 1) * 32 - player.UP + 0
                player.direction_y = 0

        return dx, dy

    def check_wall(self, player: Player, dx: float, dy: float) -> (float, float):
        """
        Также проверяет столкновение, только теперь с объектами.
        (Просто не все стены можно сделать из кубиков карты.
        :param player: Основной игрок
        :param dx: Дельта X
        :param dy: Дельта Y
        :return: Обновленные dx, dy
        """
        if not self.wall:
            return dx, dy

        left, right, up, down = player.help_func(dx, 0)
        if dx > 0:
            for wall in self.wall.objects:
                if wall.x < right < wall.x + wall.width and \
                        (wall.y < up < wall.y + wall.height or wall.y < down < wall.y + wall.height):
                    dx = 0
                    player.pos_x = wall.x - player.RIGHT - 1
                    player.direction_x = 0
                    break
        elif dx < 0:
            for wall in self.wall.objects:
                if wall.x < left < wall.x + wall.width and \
                        (wall.y < up < wall.y + wall.height or wall.y < down < wall.y + wall.height):
                    dx = 0
                    player.pos_x = wall.x + wall.width - player.LEFT + 0
                    player.direction_x = 0
                    break

        left, right, up, down = player.help_func(0, dy)
        if dy > 0:
            for wall in self.wall.objects:
                if wall.y < down < wall.y + wall.height and \
                        (wall.x < left < wall.x + wall.width or wall.x < right < wall.x + wall.width):
                    dy = 0
                    player.pos_y = wall.y - player.DOWN - 1
                    player.direction_y = 0
                    break
        elif dy < 0:
            for wall in self.wall.objects:
                if wall.y < up < wall.y + wall.height and \
                        (wall.x < left < wall.x + wall.width or wall.x < right < wall.x + wall.width):
                    dy = 0
                    player.pos_y = wall.y + wall.height - player.UP + 0
                    player.direction_y = 0
                    break

        return dx, dy

    def start_pos_hero(self, player: Player):
        """
        Ставит игрока на начальную позицию.
        :param player: Основной игрок
        :return: None
        """
        if player.pos_x == -1 or player.pos_y == -1:
            player.pos_x = self.start_x
            player.pos_y = self.start_y
        player.level = self.level
