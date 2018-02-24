#!/usr/bin/env python3

from direct.showbase.Audio3DManager import Audio3DManager

from Scenes.BaseScene import BaseScene


class Game(BaseScene):
    def __init__(self, root_node,  mode):
        self.root_node = root_node.attachNewNode('Game')
        self.mode = mode

        base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)
