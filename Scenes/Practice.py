#!/usr/bin/env python3

from panda3d.core import Vec3, BitMask32, DirectionalLight
from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape, BulletBoxShape,\
    BulletTriangleMeshShape, BulletTriangleMesh

from direct.gui.OnscreenText import OnscreenText

from Utils.format import hex_to_rgb
from Utils.geom import bullet_shape_from
from App import prefab, Gui
from App.Characters import Player
from App.Physics import World
from Scenes.BaseScene import BaseScene


class Practice(BaseScene):
    def __init__(self, root_node):
        BaseScene.__init__(self)

        self.root_node = root_node

        settings = {
            'key_forward': 'w',
            'key_left': 'a',
            'key_back': 's',
            'key_right': 'd',
            'key_crouch': 'lcontrol',
            'key_jump': 'space',
            'key_ability1': 'lshift',
            'key_ability2': 'e',
            'key_ultimate': 'q',
            'key_fire1': 'mouse1',
            'key_fire2': 'mouse3',
            'mouse_sensitivity': 75,
            'invert_pitch': False
        }

        self.skybox = prefab.skybox('maps/practice/tex/sea')

        self.physics = World()
        self.physics.node.reparentTo(self.root_node)

        self.player = Player(self.physics.world, root_node, 'Player')
        self.player.attach_controls(settings)
        self.player.set_camera(base.camera)
        self.player.char.setPos(0, 0, 0)

        self.char_marks = Gui.CharMarks()
        self.hud = Gui.HUD()

        self.load_scene()

    def destroy(self):
        self.esc_handler()
        self.char_marks.destroy()
        self.pause_menu.destroy()
        self.hud.destroy()
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
        # ground
        sandbox = loader.loadModel('maps/practice/sandbox')
        geom = sandbox.findAllMatches('**/+GeomNode')[0].node().getGeom(0)
        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        np = self.root_node.attachNewNode(BulletRigidBodyNode('Mesh'))
        np.node().addShape(shape)
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

        moon = DirectionalLight('moon')
        moon.setColor(hex_to_rgb('ffffff'))
        moon.setShadowCaster(True, 2048, 2048)
        moon_np = self.root_node.attachNewNode(moon)
        moon_np.setPos(5, 5, 10)
        moon_np.lookAt(0, 0, 0)
        self.root_node.setLight(moon_np)

        # dynamic sphere
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Box'))
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
        np = self.root_node.attachNewNode(BulletRigidBodyNode('Box'))
        np.node().addShape(BulletBoxShape(Vec3(0.5, 0.5, 0.5)))
        np.setPos(1, 2, 0.8)
        self.physics.world.attachRigidBody(np.node())

        box = loader.loadModel('geometry/box')
        box.reparentTo(np)

        self.char_marks.add('static', box, OnscreenText(text='static', scale=0.08), 0.5)
