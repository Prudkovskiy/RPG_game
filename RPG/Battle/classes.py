import random
# в качестве структур данных я брал словари
__all__ = ['HelpClass', 'Hero', 'Enemy', 'Monster', 'Attack', 'Defence']

class HelpClass:
    def __init__(self, heroes):

        self.heroes = heroes

    def get_alive_heroes(self):
        return [i for i in self.heroes if i.alive is True]


class Hero:

    def __init__(self, name, hp, mp, sp, at_list, df_list):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.sp = sp
        self.at_list = at_list  # кортеж с объектами Attack
        self.df_list = df_list  # кортеж с объектами Defense
        self.alive = True

    def to_list(self, key: str):
        return [
            self.name, key, self.hp, self.hp, self.mp, self.mp, self.sp, self.sp,
            self.at_list[0].name, self.at_list[0].size, self.at_list[0].cost,
            self.at_list[0].atr_type, self.at_list[0].defense,
            self.at_list[1].name, self.at_list[1].size, self.at_list[1].cost,
            self.at_list[1].atr_type, self.at_list[1].defense,
            self.df_list[0].name, self.df_list[0].size,
            self.df_list[1].name, self.df_list[1].size
        ]

    def __str__(self):
        return 'name:{},hp: {},mp: {},sp: {}'.format(self.name, self.hp, self.mp, self.sp)

    def get_hp(self):
        return self.hp

    def hp_change(self, attack):
        defense = 0
        for i in self.df_list:
            if i.name == attack.defense:
                defense = i.size
            else:
                defense = 0
        self.hp -= (1 - defense * 0.01) * attack.size  # сюда можно заносить изменения в расчете урона
        if self.hp <= 0:
            self.alive = False


    # непосредственно расчет атаки
    def attack(self, monster, attack):
        print(monster)
        print('name: {} sp: {} mp: {}'.format(self.name, self.sp, self.mp))
        if attack.atr_type == 'sp' and attack.cost <= self.sp:
            self.sp -= attack.cost
            monster.hp_change(attack)
        if attack.atr_type == 'mp' and attack.cost <= self.mp:
            self.mp -= attack.cost
            monster.hp_change(attack)
        print(monster)
        print('name: {} sp: {} mp: {}'.format(self.name, self.sp, self.mp))
        print(attack)


class Enemy:
    def __init__(self, monsters):
        self.monsters = monsters

    def get_alive_monsters(self):
        return [i for i in self.monsters if i.alive is True]

    def choose_random_monster(self):
        return random.choice(self.get_alive_monsters())


class Monster:

    def __init__(self, name, hp, mp, sp, at_list, df_list):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.sp = sp
        self.at_list = at_list # кортеж с объектами Attack
        self.df_list = df_list # кортеж с объектами Defense
        self.alive = True

    def __str__(self):
        return 'name: {}, hp: {},mp: {},sp: {}'.format(self.name, self.hp, self.mp, self.sp)

    def get_hp(self):
        return self.hp

    def choose_random_attack(self):
        i = random.choice(self.at_list)
        return i

    def hp_change(self, attack):
        defense = 0
        for i in self.df_list:
            if i.name == attack.defense:
                defense = i.size
            else:
                defense = 0
        self.hp -= (1 - defense * 0.01) * attack.size  # сюда можно заносить изменения в расчете урона
        if self.hp <= 0:
            self.alive = False

    def attack(self, heroes):
        low_hp = sorted(heroes, key=lambda hro: hro.get_hp())[0:2] # рандомный выбор из двух героев с наименьшим хп
        # Вот тут ошибка из-за пустого списка
        try:
            hero = random.choice(low_hp)
        except IndexError:
            raise IndexError
        print(hero)
        print('name: {} sp: {} mp: {}'.format(self.name, self.sp, self.mp))
        attack = self.choose_random_attack()
        if attack.atr_type == 'sp' and attack.cost <= self.sp:
            self.sp -= attack.cost
            hero.hp_change(attack)
        if attack.atr_type == 'mp' and attack.cost <= self.mp:
            self.mp -= attack.cost
            hero.hp_change(attack)

        print(hero)
        print('name: {} sp: {} mp: {}'.format(self.name, self.sp, self.mp))
        print(attack)

        return hero.alive, hero.name, attack.name


class Attack:
    def __init__(self, name, size, cost, atr_type, defense, features=None):
        self.name = name
        self.size = size
        self.cost = cost
        self.atr_type = atr_type
        self.defense = defense # имя соотв защиты
        self.features = features

    def __str__(self):
        return '{}'.format(self.name)


class Defence:
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def __str__(self):
        return '{}'.format(self.name)







