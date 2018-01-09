import unittest
from Runner import *
from battle import *


class BattlePlayerTest(unittest.TestCase):

    def setUp(self):
        self.hero = BattlePlayer('images/heros/Healer.png', (100, 100), 32, 32, 3, 1)
        # Position = (84, 84)

    def test_move(self):
        self.hero.move(10, -10)
        self.assertEqual(self.hero.pos_x, 94)
        self.assertEqual(self.hero.pos_y, 74)

    def test_get_pos(self):
        self.hero.move(10, -10)
        self.assertEqual(self.hero.get_pos(), (94, 74))

suite = unittest.defaultTestLoader.loadTestsFromTestCase(BattlePlayerTest)
unittest.TextTestRunner().run(suite)


class BattleSceneTest(unittest.TestCase):

    def setUp(self):
        class TestHero:
            def __init__(self):
                self.hp = 10

        obj = TestHero()
        pygame.init()
        screen = pygame.display.set_mode((640, 490))
        self.scene = BattleScene(screen,
                                 'images/background/lower/Castle.png',
                                 'images/background/upper/Brick.png',
                                 ({'name': 'healer', 'object': obj}, ),
                                 (None,
                                  {'type': 'reddragon', 'object': obj}))

    def test_heros_dict(self):
        self.assertTrue(self.scene.heros['usagi'] == None)
        self.assertFalse(self.scene.heros['healer'] == None)
        self.assertTrue(self.scene.heros['neko'] == None)
        self.assertTrue(self.scene.heros['snake'] == None)

    def test_enemies_dict(self):
        self.assertTrue(self.scene.enemies[1] == None)
        self.assertFalse(self.scene.enemies[2] == None)
        self.assertTrue(self.scene.enemies[3] == None)
        self.assertTrue(self.scene.enemies[4] == None)

    def test_heros_hp(self):
        self.assertEqual(self.scene.start_heros_hp['healer'], 10)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(BattleSceneTest)
unittest.TextTestRunner().run(suite)


class moveTest(unittest.TestCase):

    def setUp(self):
        class TestHero:
            def __init__(self):
                self.hp = 10

        obj = TestHero()
        pygame.init()
        screen = pygame.display.set_mode((640, 490))
        self.scene = BattleScene(screen,
                                 'images/background/lower/Castle.png',
                                 'images/background/upper/Brick.png',
                                 ({'name': 'healer', 'object': obj}, ))

    def test_move_left(self):
        # Healer start position = (464, 254)
        move(self.scene, 'healer', 'left')
        self.assertEqual(self.scene.heros['healer'].get_pos(), (414, 254))

    def test_move_right(self):
        # Healer start position = (464, 254)
        move(self.scene, 'healer', 'right')
        self.assertEqual(self.scene.heros['healer'].get_pos(), (514, 254))

suite = unittest.defaultTestLoader.loadTestsFromTestCase(moveTest)
unittest.TextTestRunner().run(suite)
