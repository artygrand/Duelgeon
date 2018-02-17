#!/usr/bin/env python3

from panda3d.core import Texture


def hex_to_rgb(value, alpha=1, brightness=1):
    return tuple(int(value[i:i + 2], 16)/255.0*brightness for i in (0, 2, 4)) + (alpha,)


def clamp_texture(textures):
    def as_clamp(t):
        t = loader.loadTexture(t)
        t.setWrapU(Texture.WM_clamp)
        t.setWrapV(Texture.WM_clamp)

        return t

    if type(textures) is str:
        new = as_clamp(textures)
    else:
        new = ()
        for tex in textures:
            new += (as_clamp(tex),)

    return new
