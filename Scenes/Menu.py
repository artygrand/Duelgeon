#!/usr/bin/env python3

from math import *

from panda3d.core import TextNode, DirectionalLight, AmbientLight, PerspectiveLens, Texture
from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor

from Scenes.BaseScene import BaseScene
from Managers.Menu import MM
from Game import prefab
from Utils.format import hex_to_rgb, clamp_texture


class Menu(BaseScene):
    music = None
    ambientSound = None

    main = None
    modes = None
    options = None

    skybox = None

    def __init__(self, root_node):
        BaseScene.__init__(self)

        self.root_node = root_node

        self.manager = MM(self)

        self.audio()
        self.main_frame()
        self.modes_frame()
        self.options_frame()
        self.background()

        self.manager.request('Main')

    def audio(self):
        self.music = loader.loadMusic("audio/music/menu.wav")
        self.music.setLoop(True)
        self.music.play()

        self.ambientSound = loader.loadSfx("audio/sfx/bonfire.mp3")
        self.ambientSound.setLoop(True)
        self.ambientSound.play()
        self.ambientSound.setVolume(.7)

    def main_frame(self):
        tex = clamp_texture('gui/menu-frame.png')
        self.main = DirectFrame(frameSize=(-.4, .4, 1, -1), pos=(base.a2dLeft+.4, 0, 0), frameTexture=tex)
        self.main.setTransparency(1)
        self.main.hide()

        logo = OnscreenImage(image='gui/logo.png', pos=(0, 0, .75), scale=(.30, 1, .15), parent=self.main)
        logo.setTransparency(1)

        button = loader.loadModel('gui/menu-button')
        clamp_texture(('gui/menu-button-hover.png', 'gui/menu-button-click.png'))
        pos = .0
        for cmd, text in {'Play': 'Play', 'Training': 'Training', 'Heroes': 'Heroes',
                          'Options': 'Options', 'Exit': 'Exit'}.items():
            DirectButton(
                text=text,
                scale=0.6,
                pos=(-.35, 0, pos),
                text0_fg=(1, 1, 1, 1),
                text2_fg=(0, 0, 0, 1),
                text1_fg=(.6, .6, .6, 1),
                text_scale=0.1,
                text_align=TextNode.ALeft,
                text_pos=(0.06, -0.03),
                command=base.messenger.send,
                extraArgs=['Menu-' + cmd],
                rolloverSound=None,
                clickSound=None,
                relief=None,
                geom=(button.find('**/button'), button.find('**/button-click'),
                      button.find('**/button-hover'), button.find('**/button-disabled')),
                frameSize=(-.1, 1, .1, -.1),
                parent=self.main
            )
            pos -= .1

    def modes_frame(self):
        self.modes = DirectFrame(frameSize=(base.a2dLeft + .05, base.a2dRight - .05, .95, -.95),
                                 frameColor=(0, 0, 0, .6))
        self.modes.setTransparency(1)
        self.modes.hide()

        self.back_button('modes')

        pos = base.a2dRight / 4
        for cmd, text in {'Arcade': 'Arcade', 'Hardcore': 'Hardcore',
                          'Coop': 'Coop', 'Versus': 'Versus'}.items():
            DirectButton(
                text=text,
                scale=0.08,
                frameSize=(-4, 4, 11, -1),
                pos=(base.a2dLeft + pos, 0, -.3),
                command=base.messenger.send,
                extraArgs=['Play-' + cmd],
                rolloverSound=None,
                clickSound=None,
                # relief=None,
                parent=self.modes
            )
            pos += base.a2dRight / 2

    def options_frame(self):
        self.options = DirectFrame(frameSize=(base.a2dLeft + .05, base.a2dRight - .05, .95, -.95),
                                   frameColor=(0, 0, 0, .6))
        self.options.setTransparency(1)
        self.options.hide()

        self.back_button('options')

    def back_button(self, frame):
        DirectButton(
            text='Back',
            scale=0.07,
            pos=(base.a2dRight - .2, 0, -.9),
            text0_fg=(.6, .6, .6, 1),
            text1_fg=(1, 1, 1, 1),
            text2_fg=(1, 1, 1, 1),
            command=base.messenger.send,
            extraArgs=['Menu-Back'],
            rolloverSound=None,
            clickSound=None,
            relief=None,
            parent=getattr(self, frame)
        )

    def show(self, frame):
        getattr(self, frame).show()

    def hide(self, frame):
        getattr(self, frame).hide()

    def destroy(self):
        self.root_node.removeNode()
        self.skybox.removeNode()

        self.main.removeNode()
        self.modes.removeNode()
        self.options.removeNode()

        self.music.stop()  # or delete?
        self.ambientSound.stop()

        base.taskMgr.remove('spin_camera')
        base.taskMgr.remove('bonfire_light_pos')

    def background(self):
        self.skybox = prefab.skybox('maps/menu/tex/mountains')

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

        bonfire = prefab.Bonfire(scene)
        bonfire.holder.setPos(0, -.08, .1)

        ambient = AmbientLight('alight')
        ambient.setColor(hex_to_rgb('141414'))
        ambient_np = scene.attachNewNode(ambient)
        scene.setLight(ambient_np)

        def spin_camera_task(task):
            angle_degrees = task.time * 2.0
            if angle_degrees > 360:
                angle_degrees -= 360

            angle_radians = angle_degrees * (pi / 180)
            base.camera.setPos(5 * sin(angle_radians), -5 * cos(angle_radians), 1)
            base.camera.setHpr(angle_degrees, 4, 0)

            return task.cont

        base.taskMgr.add(spin_camera_task, 'spin_camera')

    def esc_handler(self):
        if self.manager.state != 'Main':
            self.manager.request('Main')
