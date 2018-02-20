#!/usr/bin/env python3

from panda3d.core import NodePath, Vec3
from panda3d.bullet import BulletWorld, BulletDebugNode


class World:
    def __init__(self):
        self.node = NodePath('World')
        self.debug_node = self.node.attachNewNode(BulletDebugNode('Debug'))

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debug_node.node())

        self.resume()
        base.accept('f1', self.debug)

    def resume(self):
        base.taskMgr.add(self.update, 'update_world')

    def pause(self):
        base.taskMgr.remove('update_world')

    def update(self, task):
        self.world.doPhysics(globalClock.getDt())

        return task.cont

    def debug(self):
        if self.debug_node.isHidden():
            self.debug_node.show()
            base.setFrameRateMeter(True)
        else:
            self.debug_node.hide()
            base.setFrameRateMeter(False)
