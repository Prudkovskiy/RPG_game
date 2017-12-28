#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TileMap loader for python for Tiled, a generic tile map editor
from http://mapeditor.org/ .
It loads the \*.tmx files produced by Tiled.


"""
__all__ = ["tmxreader"]

from . import tmxreader
try:
    from . import helperspygame
    __all__.append("helperspygame")
except:
    pass

try:
    from . import helperspyglet
    __all__.append("helperspyglet")
except:
    pass


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
__version__ = tmxreader.__version__
__author__ = 'DR0ID @ 2009-2011'


#-------------------------------------------------------------------------------

