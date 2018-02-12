from random import *

from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import PointLight, Texture

from Utils.format import hex_to_rgb


def skybox(texture):
    box = loader.loadModel('geometry/skybox')
    textures = {p: loader.loadTexture(texture + '_' + p + '.png') for p in ['u', 'l', 'f', 'r', 'b', 'd']}

    for key, tex in textures.items():
        tex.setWrapU(Texture.WM_clamp)
        tex.setWrapV(Texture.WM_clamp)
        box.find('**/' + key).setTexture(tex)

    box.setScale(512)
    box.setBin('background', 1)
    box.setDepthWrite(0)
    box.setLightOff()
    box.clearFog()
    box.setCompass()

    box.reparentTo(base.camera)

    return box


class Bonfire:
    po = [0, 0, .4]  # light position origin
    pd = [0, 0, 0]  # light position delta
    ld = 0  # light lightness delta

    def __init__(self, parent, color='ff8033'):
        self.holder = parent.attachNewNode('holder')
        self.co = hex_to_rgb(color)

        self.plight = PointLight('bonfire')
        self.plight.setColor(self.co)
        self.plight.setAttenuation((1, 0, 1))
        self.plight.setShadowCaster(True, 2048, 2048)

        self.plnp = self.holder.attachNewNode(self.plight)
        parent.setLight(self.plnp)

        floater = self.holder.attachNewNode('particle root')
        fire = ParticleEffect()
        fire.loadConfig('assets/fx/bonfire.ptf')
        fire.start(parent=floater, renderParent=parent)

        base.taskMgr.add(self.light_pos_task, 'bonfire_light_pos')

    def light_pos_task(self, task):
        cx, cy, cz = self.plnp.getPos()

        if task.frame % 10 == 0:
            self.pd[0] = (self.po[0] + uniform(-.05, .05) - cx) / 10
            self.pd[1] = (self.po[1] + uniform(-.05, .05) - cy) / 10
            self.pd[2] = (self.po[2] + uniform(-.03, .03) - cz) / 10

        self.plnp.setPos(cx + self.pd[0], cy + self.pd[1], cz + self.pd[2])

        if task.frame % 5 == 0:
            self.ld = uniform(-.1, .1)

        self.plight.setColor((self.co[0] + self.ld, self.co[1] + self.ld, self.co[2] + self.ld, self.co[3]))

        return task.cont
