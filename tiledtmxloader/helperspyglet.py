# -*- coding: utf-8 -*-

"""
> Overview
This program contains a sample implementation for loading a map produced
by Tiled in pyglet. The script can be run on its own to demonstrate its
capabilities, or the script can be imported to use its functionality. Users
will hopefully use the ResourceLoaderPyglet already provided in this.
Tiled may be found at http://mapeditor.org/

> Demo Controls
Holding the arrow keys scrolls the map.
Holding the left shift key makes you scroll faster.
Pressing the Esc key closes the program.

> Demo Features
The map is fully viewable by scrolling.
You can scroll outside of the bounds of the map.
All visible layers are loaded and displayed.
Transparency is supported. (Nothing needed to be done for this.)
Minimal OpenGL used. (Less of a learning curve.)

"""

# Versioning scheme based on: http://en.wikipedia.org/wiki/Versioning#Designating_development_stage
#
#   +-- api change, probably incompatible with older versions
#   |     +-- enhancements but no api change
#   |     |
# major.minor[.build[.revision]]
#                |
#                +-|* 0 for alpha (status)
#                  |* 1 for beta (status)
#                  |* 2 for release candidate
#                  |* 3 for (public) release
#
# For instance:
#     * 1.2.0.1 instead of 1.2-a
#     * 1.2.1.2 instead of 1.2-b2 (beta with some bug fixes)
#     * 1.2.2.3 instead of 1.2-rc (release candidate)
#     * 1.2.3.0 instead of 1.2-r (commercial distribution)
#     * 1.2.3.5 instead of 1.2-r5 (commercial distribution with many bug fixes)

__revision__ = "$Rev: 115 $"
__version__ = "3.0.0." + __revision__[6:-2]
__author__ = 'DR0ID @ 2009-2011'


#  -----------------------------------------------------------------------------


import copy
import os.path
import sys

import pyglet

from . import tmxreader


#  -----------------------------------------------------------------------------

# [20:31]	bjorn: Of course, for fastest rendering, you would combine the used 
# tiles into a single texture and set up arrays of vertex and texture coordinates.
# .. so that the video card can dump the map to the screen without having to 
# analyze the tile data again and again.

class ResourceLoaderPyglet(tmxreader.AbstractResourceLoader):
    """Loads all tile images and lays them out on a grid.

    Unlike the AbstractResourceLoader this class derives from, no overridden
    methods use a colorkey parameter. A colorkey is only useful for pygame.
    This loader adds its own pyglet-specific parameter to deal with
    pyglet.image.load's capability to work with file-like objects.
    
    """

    def load(self, tile_map):
        tmxreader.AbstractResourceLoader.load(self, tile_map)
        # ISSUE 17: flipped tiles
        for layer in self.world_map.layers:
            for gid in layer.decoded_content:
                if gid not in self.indexed_tiles:
                    if gid & self.FLIP_X or gid & self.FLIP_Y:
                        image_gid = gid & ~(self.FLIP_X | self.FLIP_Y)
                        offx, offy, img = self.indexed_tiles[image_gid]
                        # TODO: how to flip it? this does mix textures and image classes
                        img = copy.deepcopy(img)
                        tex = img.get_texture()
                        tex.anchor_x = tex.width // 2
                        tex.anchor_y = tex.height // 2
                        tex2 = tex.get_transform(bool(gid & self.FLIP_X), bool(gid & self.FLIP_Y))
                        # img2 = pyglet.image.ImageDataRegion(img.x, img.y, tex2.width, tex2.height, tex2.image_data))
                        tex.anchor_x = 0
                        tex.anchor_y = 0
                        self.indexed_tiles[gid] = (offx, offy, tex2)

    def _load_image(self, filename, fileobj=None):
        """Load a single image.

        Images are loaded only once. Subsequence loads call upon a cache.

        :Parameters:
            filename : string
                Path to the file to be loaded.
            fileobj : file
                A file-like object which pyglet can decode.

        :rtype: A subclass of AbstractImage.

        """
        img = self._img_cache.get(filename, None)
        if img is None:
            if fileobj:
                img = pyglet.image.load
            else:
                img = pyglet.image.load
            self._img_cache[filename] = img
        return img

    def _load_image_part(self, filename, x, y, w, h):
        """Load a section of an image and returns its ImageDataRegion."""
        return self._load_image(filename).get_region(x, y, w, h)

    def _load_image_parts(self, filename, margin, spacing, tile_width, tile_height, colorkey=None):
        """Load different tile images from one source image.

        :Parameters:
            filename : string
                Path to image to be loaded.
            margin : int
                The margin around the image.
            spacing : int
                The space between the tile images.
            tilewidth : int
                The width of a single tile.
            tileheight : int
                The height of a single tile.
            colorkey : ???
                Unused. (Intended for pygame.)

        :rtype: A list of images.
        
        """
        source_img = self._load_image(filename)
        # ISSUE 16 fixed wrong sized tilesets
        height = (source_img.height // tile_height) * tile_height
        width = (source_img.width // tile_width) * tile_width
        images = []
        # Reverse the map column reading to compensate for pyglet's y-origin.
        for y in range(height - tile_height, margin - tile_height, -tile_height - spacing):
            for x in range(margin, width, tile_width + spacing):
                img_part = self._load_image_part(filename, x, y - spacing, tile_width, tile_height)
                images.append(img_part)
        return images

    def _load_image_file_like(self, file_like_obj):
        """Loads a file-like object and returns its subclassed AbstractImage."""
        # TODO: Ask myself why this extra indirection is necessary.
        return self._load_image(file_like_obj, file_like_obj)


#  -----------------------------------------------------------------------------


def demo_pyglet(file_name):
    """Demonstrates loading, rendering, and traversing a Tiled map in pyglet.
    
    TODO:
    Maybe use this to put topleft as origin:
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        glOrtho(0.0, (double)mTarget->w, (double)mTarget->h, 0.0, -1.0, 1.0);

    """

    import pyglet
    from pyglet.gl import glTranslatef, glLoadIdentity

    world_map = tmxreader.TileMapParser().parse_decode(file_name)
    # delta is the x/y position of the map view.
    # delta is a list so that it can be accessed from the on_draw method of
    # window and the update function. Note that the position is in integers to
    # match Pyglet Sprites. Using floating-point numbers causes graphical
    # problems. See http://groups.google.com/group/pyglet-users/browse_thread/thread/52f9ae1ef7b0c8fa?pli=1
    delta = [200, -world_map.pixel_height+150]
    frames_per_sec = 1.0 / 30.0
    window = pyglet.window.Window()

    @window.event
    def on_draw():
        window.clear()
        # Reset the "eye" back to the default location.
        glLoadIdentity()
        # Move the "eye" to the current location on the map.
        glTranslatef(delta[0], delta[1], 0.0)
        # TODO: [21:03]	thorbjorn: DR0ID_: You can generally determine the range of tiles that are visible before your drawing loop, which is much faster than looping over all tiles and checking whether it is visible for each of them.
        # [21:06]	DR0ID_: probably would have to rewrite the pyglet demo to use a similar render loop as you mentioned
        # [21:06]	thorbjorn: Yeah.
        # [21:06]	DR0ID_: I'll keep your suggestion in mind, thanks
        # [21:06]	thorbjorn: I haven't written a specific OpenGL renderer yet, so not sure what's the best approach for a tile map.
        # [21:07]	thorbjorn: Best to create a single texture with all your tiles, bind it, set up your vertex arrays and fill it with the coordinates of the tiles currently on the screen, and then let OpenGL draw the bunch.
        # [21:08]	DR0ID_: for each layer?
        # [21:08]	DR0ID_: yeah, probably a good approach
        # [21:09]	thorbjorn: Ideally for all layers at the same time, if you don't have to draw anything in between.
        # [21:09]	DR0ID_: well, the NPC and other dynamic things need to be drawn in between, right?
        # [21:09]	thorbjorn: Right, so maybe once for the bottom layers, then your complicated stuff, and then another time for the layers on top.

        batch.draw()

    keys = pyglet.window.key.KeyStateHandler()
    window.push_handlers(keys)
    resources = ResourceLoaderPyglet()
    resources.load(world_map)

    def update(dt):
        # The speed is 3 by default.
        # When left Shift is held, the speed increases.
        # The speed interpolates based on time passed, so the demo navigates
        # at a reasonable pace even on huge maps.
        speed = (3 + keys[pyglet.window.key.LSHIFT] * 6) * \
                int(dt / frames_per_sec)
        if keys[pyglet.window.key.LEFT]:
            delta[0] += speed
        if keys[pyglet.window.key.RIGHT]:
            delta[0] -= speed
        if keys[pyglet.window.key.UP]:
            delta[1] -= speed
        if keys[pyglet.window.key.DOWN]:
            delta[1] += speed

    # Generate the graphics for every visible tile.
    batch = pyglet.graphics.Batch()
    sprites = []
    for group_num, layer in enumerate(world_map.layers):
        if not layer.visible:
            continue
        if layer.is_object_group:
            # This is unimplemented in this minimal-case example code.
            # Should you as a user of tmxreader need this layer,
            # I hope to have a separate demo using objects as well.
            continue
        group = pyglet.graphics.OrderedGroup(group_num)
        for ytile in range(layer.height):
            for xtile in range(layer.width):
                image_id = layer.content2D[xtile][ytile]
                if image_id:
                    image_file = resources.indexed_tiles[image_id][2]
                    # The loader needed to load the images upside-down to match
                    # the tiles to their correct images. This reversal must be
                    # done again to render the rows in the correct order.
                    sprites.append(pyglet.sprite.Sprite(image_file,
                        world_map.tilewidth * xtile,
                        world_map.tileheight * (layer.height - ytile),
                        batch=batch, group=group))

    pyglet.clock.schedule_interval(update, frames_per_sec)
    pyglet.app.run()


#  -----------------------------------------------------------------------------

if __name__ == '__main__':
    # import cProfile
    # cProfile.run('main()', "stats.profile")
    # import pstats
    # p = pstats.Stats("stats.profile")
    # p.strip_dirs()
    # p.sort_stats('time')
    # p.print_stats()
    if len(sys.argv) == 2:
        demo_pyglet(sys.argv[1])
    else:
        print(('Usage: python %s your_map.tmx' % os.path.basename(__file__)))


