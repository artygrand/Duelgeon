#!/usr/bin/env python3

from math import *

from panda3d.core import DirectionalLight, AmbientLight, PerspectiveLens, Texture

from direct.actor.Actor import Actor

from Scenes.BaseScene import BaseScene
from App import prefab
from Utils.format import hex_to_rgb


class Menu(BaseScene):
    music = None
    ambientSound = None

    def __init__(self, root_node):
        BaseScene.__init__(self)

        self.root_node = root_node.attachNewNode('Menu')

        self.skybox = prefab.skybox('maps/menu/tex/mountains')
        self.audio()
        self.background()

    def audio(self):
        self.music = loader.loadMusic('audio/music/menu.wav')
        self.music.setLoop(True)
        self.music.play()

        self.ambientSound = loader.loadSfx('audio/sfx/bonfire.mp3')
        self.ambientSound.setLoop(True)
        self.ambientSound.play()
        self.ambientSound.setVolume(.7)

    def destroy(self):
        self.root_node.removeNode()
        self.skybox.removeNode()

        self.music.stop()  # or delete?
        self.ambientSound.stop()

        base.taskMgr.remove('spin_camera')
        self.bonfire.destroy()

    def background(self):
        scene = loader.loadModel('maps/menu/terrain')
        scene.reparentTo(self.root_node)

        actor = Actor('actors/char', {'walk': 'actors/char-walk', 'hands': 'actors/char-hands'})
        actor.reparentTo(scene)
        actor.setPos(0, 1, 0)

        moon = DirectionalLight('moon')
        moon.setColor(hex_to_rgb('4d5acc', brightness=.2))
        moon.setShadowCaster(True, 2048, 2048)
        moon_np = scene.attachNewNode(moon)
        moon_np.setPos(-5, -5, 10)
        moon_np.lookAt(0, 0, 0)
        scene.setLight(moon_np)

        self.bonfire = prefab.Bonfire(scene)
        self.bonfire.holder.setPos(0, -.08, .1)

        ambient = AmbientLight('alight')
        ambient.setColor(hex_to_rgb('141414'))
        ambient_np = scene.attachNewNode(ambient)
        scene.setLight(ambient_np)

        def spin_camera_task(task):
            angle_degrees = task.time * 2.0
            if angle_degrees > 360:
                angle_degrees -= 360

            angle_radians = angle_degrees * (pi / 180)
            base.camera.setPos(3 * sin(angle_radians), -3 * cos(angle_radians), 1)
            base.camera.setHpr(angle_degrees, 4, 0)

            return task.cont

        base.taskMgr.add(spin_camera_task, 'spin_camera')
