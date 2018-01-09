import pyganim
__all__ = ['BattlePlayer', 'BattleEnemy']


class BattlePlayer:
    def __init__(self, img, position=(16, 16), width=32, height=32, num=3, st=0):
        self.img_width = width
        self.img_height = height
        anim_types = ['front', 'left', 'right', 'back']
        self.anim_objs = {}
        self.standing = {}
        i = 0
        for anim_type in anim_types:
            rects = [(num * width, i * height, width, height) for num in range(num)]
            all_images = pyganim.getImagesFromSpriteSheet(img, rects=rects)
            self.standing[anim_type] = all_images[st]
            frames = list(zip(all_images, [100] * len(all_images)))
            self.anim_objs[anim_type] = pyganim.PygAnimation(frames)
            i += 1

        self.move_conductor = pyganim.PygConductor(self.anim_objs)

        self.pos_x, self.pos_y = position
        self.pos_x -= self.standing['front'].get_width() / 2
        self.pos_y -= self.standing['front'].get_height() / 2


    def move(self, dx, dy):
        self.pos_x += dx
        self.pos_y += dy

    def get_pos(self):
        return self.pos_x, self.pos_y


class BattleEnemy:
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