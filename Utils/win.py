#!/usr/bin/env python3

from panda3d.core import WindowProperties, LVector3, PerspectiveLens


def hide_cursor():
    props = WindowProperties()
    props.setCursorHidden(True)
    base.win.requestProperties(props)


def show_cursor():
    props = WindowProperties()
    props.setCursorHidden(False)
    base.win.requestProperties(props)


def center_cursor():
    return base.win.movePointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2))


def change_resolution(w, h):
    props = WindowProperties()
    props.setSize(int(w), int(h))
    base.win.requestProperties(props)


def toggle_fullscreen(full=None):
    windowed = not base.win.isFullscreen()

    if full is not None and full != windowed:
        return

    props = WindowProperties(base.win.getProperties())
    props.setFullscreen(windowed)
    base.win.requestProperties(props)
