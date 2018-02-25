#!/usr/bin/env python3

from panda3d.core import Vec3
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState

from Utils import win
from App.Options import Options
from App.Characters import Dummy


class Controller(DirectObject):
    def __init__(self, char):
        DirectObject.__init__(self)

        self.camera = None  # TODO use for sniper zoom
        self.dummy = Dummy()
        self.char = char
        self.watch_tokens = []

        self.bind_keys()

    def destroy(self):
        self.unbind_keys()

    def resume(self):
        self.bind_keys()

    def pause(self):
        self.unbind_keys()
        self.acceptOnce('Resume-game', self.resume)

    def bind_keys(self, free=False):
        self.acceptOnce('Pause-game', self.pause)
        base.taskMgr.add(self.keyboard_watcher, 'player_keyboard_watcher')

        self.watch_tokens.append(inputState.watchWithModifiers('forward', Options.key_forward))
        self.watch_tokens.append(inputState.watchWithModifiers('back', Options.key_back))
        self.watch_tokens.append(inputState.watchWithModifiers('left', Options.key_left))
        self.watch_tokens.append(inputState.watchWithModifiers('right', Options.key_right))

        if free:
            self.watch_tokens.append(inputState.watchWithModifiers('up', Options.key_jump))
            self.watch_tokens.append(inputState.watchWithModifiers('down', Options.key_crouch))
        else:
            self.accept(Options.key_jump, self.char.jump)
            self.accept(Options.key_crouch, self.char.crouch, [True])
            self.accept(Options.key_crouch + '-up', self.char.crouch, [False])
            self.accept(Options.key_ability1, self.char.ability1, [True])
            self.accept(Options.key_ability1 + '-up', self.char.ability1, [False])
            self.accept(Options.key_ability2, self.char.ability2, [True])
            self.accept(Options.key_ability2 + '-up', self.char.ability2, [False])
            self.accept(Options.key_ability3, self.char.ability3)

        if base.mouseWatcherNode.hasMouse():
            win.center_cursor()

            base.taskMgr.add(self.mouse_watcher, 'player_mouse_watcher', appendTask=True,
                             extraArgs=[Options.mouse_sensitivity, Options.invert_mouse])

            if not free:
                self.watch_tokens.append(inputState.watchWithModifiers('fire1', Options.key_fire1))
                self.watch_tokens.append(inputState.watchWithModifiers('fire2', Options.key_fire2))

    def unbind_keys(self):
        base.taskMgr.remove('player_keyboard_watcher')
        base.taskMgr.remove('player_mouse_watcher')

        self.ignoreAll()

        for token in self.watch_tokens:
            token.release()

    def mouse_watcher(self, sens, invert, task):
        md = base.win.getPointer(0)
        x, y = md.getX(), md.getY()

        win.center_cursor()

        self.char.omega = (base.win.getXSize() / 2 - x) * sens * 5  # TODO проверить на разных разрешениях

        delta = (base.win.getYSize() / 2 - y) * sens / 50
        delta *= [1, -1][invert]
        pitch = self.char.pitch + delta
        if pitch > 90:
            pitch = 90
        elif pitch < -90:
            pitch = -90
        self.char.pitch = pitch

        if inputState.isSet('fire1'):
            self.char.fire1()
        if inputState.isSet('fire2'):
            self.char.fire2()

        return task.cont

    def keyboard_watcher(self, task):
        m = Vec3(0, 0, 0)
        if inputState.isSet('forward'):
            m.setY(1)
        elif inputState.isSet('back'):
            m.setY(-1)
        if inputState.isSet('left'):
            m.setX(-1)
        elif inputState.isSet('right'):
            m.setX(1)
        if inputState.isSet('up'):
            m.setZ(1)
        elif inputState.isSet('down'):
            m.setZ(-1)
        self.char.movement = m

        return task.cont

    def noclip(self, on=True):
        if on and type(self.char) is Dummy or not on and type(self.dummy) is Dummy:
            return

        if on:
            self.dummy.setHpr(self.char.getHpr())
            self.dummy.setPos(self.char.getPos())

        self.dummy, self.char = self.char, self.dummy
        self.unbind_keys()
        self.bind_keys(on)

    def get_hpr(self):
        return self.char.getHpr()

    def get_pos(self):
        return self.char.getPos()

    def get_cam_pos(self):
        return self.char.getPos() + (0, 0, 1.65)

    def set_camera(self, camera):
        self.camera = camera


class Camera:
    def __init__(self, player, camera):
        self.zoomed = False
        self.normal = Options.fov
        self.zoom = Options.fov / 2
        self.speed = 200.0

        self.player = player
        self.camera = camera
        self.controller = FirstPersonCam(player, camera)

        base.taskMgr.add(self.__update, 'player_camera')

    def destroy(self):
        base.taskMgr.remove('player_camera')

    def first(self):
        self.controller = FirstPersonCam(self.player, self.camera)

    def third(self):
        self.controller = ThirdPersonCam(self.player, self.camera)

    def zoom(self, on=True):
        self.zoomed = on

    def __update(self, task):
        self.controller.update()

        fov = base.camLens.getFov()[0]
        if self.zoomed:
            fov = max(self.zoom, fov - self.speed * globalClock.getDt())
        else:
            fov = min(self.normal, fov + self.speed * globalClock.getDt())
        base.camLens.setFov(fov)

        return task.cont


class FirstPersonCam:
    def __init__(self, player, camera):
        self.player = player
        self.camera = camera

    def update(self):
        self.camera.setHpr(self.player.get_hpr())
        self.camera.setPos(self.player.get_cam_pos())


class ThirdPersonCam:
    def __init__(self, player, camera):
        self.player = player
        self.camera = camera

    def update(self):
        pass
