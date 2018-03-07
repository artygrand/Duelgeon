#!/usr/bin/env python3

from math import *

from panda3d.core import Vec3, BitMask32, DirectionalLight
from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape, BulletBoxShape

from direct.gui.OnscreenText import OnscreenText

from Utils.format import hex_to_rgb
from Utils.geom import bullet_shape_from
from App import prefab, Gui
from App.Characters import Character
from App.Physics import World
from Scenes.BaseScene import BaseScene
from App.Player import Controller, Camera
from App.Hero import get_active_hero, make_enemy


class Practice(BaseScene):
    def __init__(self, root_node):
        BaseScene.__init__(self)

        self.root_node = root_node.attachNewNode('Training')

        self.skybox = prefab.skybox('maps/practice/tex/sea')

        self.physics = World()
        self.physics.node.reparentTo(self.root_node)

        self.player = Controller(Character(self.physics.world, self.root_node, get_active_hero()))
        self.camera = Camera(self.player, base.camera)
        self.player.set_camera(self.camera)
        self.player.char.setPos(0, -1, 5)
        # self.player.char.body.up = Vec3(-1, 0, 0)
        # self.player.char.body.node.setR(-180)

        # self.enemy = AiController(Character(self.physics.world, self.root_node, make_enemy()))

        self.char_marks = Gui.CharMarks()
        self.hud = Gui.HUD()

        self.load_scene()
        self.resume()

    def destroy(self):
        BaseScene.destroy(self)
        self.char_marks.destroy()
        self.hud.destroy()
        self.root_node.removeNode()
        self.skybox.removeNode()
        self.player.destroy()

    def resume(self):
        BaseScene.resume(self)
        base.taskMgr.add(self.__update, 'update_scene')

    def pause(self):
        BaseScene.pause(self)
        base.taskMgr.remove('update_scene')

    def __update(self, task):
        dt = globalClock.getDt()
        self.physics.update(dt)
        self.player.char.update(dt)

        return task.cont

    def load_scene(self):
        # ground
        sandbox = loader.loadModel('maps/practice/sandbox')
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Mesh'))
        np.node().addShape(bullet_shape_from(sandbox))
        np.setPos(0, 0, 0)
        np.setCollideMask(BitMask32.allOn())
        self.physics.world.attachRigidBody(np.node())
        sandbox.reparentTo(np)

        moon = DirectionalLight('moon')
        moon.setColor(hex_to_rgb('ffffff'))
        moon.setShadowCaster(True, 2048, 2048)
        moon_np = self.root_node.attachNewNode(moon)
        moon_np.setPos(-5, -5, 10)
        moon_np.lookAt(0, 0, 0)
        self.root_node.setLight(moon_np)

        moon = DirectionalLight('sun')
        moon.setColor(hex_to_rgb('666666'))
        moon.setShadowCaster(True, 2048, 2048)
        moon_np = self.root_node.attachNewNode(moon)
        moon_np.setPos(5, 5, 10)
        moon_np.lookAt(0, 0, 0)
        self.root_node.setLight(moon_np)

        # dynamic sphere
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Sphere'))
        np.node().addShape(BulletSphereShape(1))
        np.node().setMass(3.0)
        np.setPos(5, 5, 2)
        self.physics.world.attachRigidBody(np.node())

        ball = loader.loadModel('geometry/ball')
        ball.reparentTo(np)

        self.char_marks.add('ball', ball, OnscreenText(text='sphere', scale=0.07), 1)

        # dynamic box
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Box'))
        np.node().addShape(BulletBoxShape(Vec3(0.5, 0.5, 0.5)))
        np.node().setMass(1.0)
        np.setPos(-1, -2, 2)
        self.physics.world.attachRigidBody(np.node())

        np.node().applyCentralImpulse((0, 2, 7))

        box = loader.loadModel('geometry/box')
        box.reparentTo(np)

        self.char_marks.add('box', box, OnscreenText(text='cube', scale=0.06), 0.5)

        # static
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Static'))
        np.node().addShape(BulletBoxShape(Vec3(0.5, 0.5, 0.5)))
        np.setPos(1, 2, 0.8)
        self.physics.world.attachRigidBody(np.node())

        box = loader.loadModel('geometry/box')
        box.reparentTo(np)

        def move_box(task):
            angle_degrees = task.time * 12.0
            if angle_degrees > 360:
                angle_degrees -= 360

            angle_radians = angle_degrees * (pi / 180)
            np.setPos(5 * sin(angle_radians), -5 * cos(angle_radians), .5)
            np.setHpr(angle_degrees, 4, 0)

            return task.cont

        base.taskMgr.add(move_box, 'move_box')

        self.char_marks.add('static', box, OnscreenText(text='static', scale=0.08), 0.5)
