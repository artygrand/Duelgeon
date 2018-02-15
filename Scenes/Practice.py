#!/usr/bin/env python3

from panda3d.core import Vec3, BitMask32
from panda3d.bullet import BulletRigidBodyNode, BulletPlaneShape, BulletSphereShape, BulletBoxShape

from Game import prefab
from Game.Characters import Player
from Game.Physics import World
from Scenes.BaseScene import BaseScene


class Practice(BaseScene):
    def __init__(self, root_node):
        self.root_node = root_node
        controls = {
            'forward': 'w',
            'left': 'a',
            'back': 's',
            'right': 'd',
            'crouch': 'lcontrol',
            'jump': 'space',
            'ability1': 'lshift',
            'ability2': 'e',
            'ultimate': 'q',
            'fire1': 'mouse1',
            'fire2': 'mouse3',
        }

        self.skybox = prefab.skybox('maps/practice/tex/sea')

        self.physics = World()
        self.physics.node.reparentTo(self.root_node)

        self.player = Player(self.physics.world, root_node)
        self.player.attach_controls(controls)
        self.player.set_camera(base.camera)

        self.load_scene()

    def destroy(self):
        self.root_node.removeNode()
        self.skybox.removeNode()
        self.player.destroy()

    def pause(self):
        self.player.pause()
        self.physics.pause()

    def resume(self):
        self.player.resume()
        self.physics.resume()

    def load_scene(self):
        # static
        box = loader.loadModel('geometry/skybox')
        box.reparentTo(self.root_node)
        box.setPos(0, 3, 0)

        # ground plane
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Ground'))
        np.node().addShape(BulletPlaneShape(Vec3(0, 0, 1), 0))
        np.setPos(0, 0, 0)
        np.setCollideMask(BitMask32.allOn())
        self.physics.world.attachRigidBody(np.node())

        # dynamic sphere
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Box'))
        np.node().addShape(BulletSphereShape(0.5))  # Vec3(0.5, 0.5, 0.5)
        np.node().setMass(1.0)
        np.setPos(0, 0, 2)
        self.physics.world.attachRigidBody(np.node())

        box = loader.loadModel('geometry/skybox')
        box.reparentTo(np)

        # dynamic box
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Box'))
        np.node().addShape(BulletBoxShape(Vec3(0.5, 0.5, 0.5)))
        np.node().setMass(1.0)
        np.setPos(-1, -2, 2)
        self.physics.world.attachRigidBody(np.node())

        box = loader.loadModel('geometry/skybox')
        box.reparentTo(np)
