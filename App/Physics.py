#!/usr/bin/env python3

from panda3d.core import NodePath, Vec3
from panda3d.bullet import BulletWorld, BulletDebugNode
from direct.showbase.DirectObject import DirectObject



class World(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)

        self.node = NodePath('World')
        self.debug_node = self.node.attachNewNode(BulletDebugNode('Debug'))

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debug_node.node())

        self.accept('f1', self.debug)

    def update(self, dt):
        self.world.doPhysics(dt)

    def debug(self):
        if self.debug_node.isHidden():
            self.debug_node.show()
            base.setFrameRateMeter(True)
        else:
            self.debug_node.hide()
            base.setFrameRateMeter(False)
