#!/usr/bin/env python3

from panda3d.core import Point2, Point3, VBase4, TextNode
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText

from App.Options import Options
from Utils.format import clamp_texture


class HasFrame:
    def __init__(self, z):
        self.frame = DirectFrame(sortOrder=z)

    def show(self):
        self.frame.show()

    def hide(self):
        self.frame.hide()

    def destroy(self):
        self.frame.destroy()


class CharMarks(HasFrame):
    chars = {}
    marks = {}
    heights = {}

    def __init__(self):
        HasFrame.__init__(self, 1)

        base.taskMgr.add(self.update, 'update char marks', 10)

    def add(self, name, char, mark, height):
        mark.reparentTo(self.frame)
        self.chars[name] = char
        self.marks[name] = mark
        self.heights[name] = height

    def remove(self, name):
        del self.chars[name]
        del self.marks[name]
        del self.heights[name]

    def update(self, task):
        for name, char in self.chars.items():
            self.marks[name].setPos(*self.get_pos(char, self.heights[name]))

        return task.cont

    def get_pos(self, node, height):
        p3 = base.cam.getRelativePoint(render, node.getPos(render))
        full = base.camLens.getProjectionMat().xform(VBase4(p3[0], p3[1], p3[2], 1.0))
        p2 = 10.0, 10.0

        if full[3] > 0:
            full3 = 1.0 / full[3]
            p2 = full[0] * full3, full[1] * full3

        pos = aspect2d.getRelativePoint(render2d, Point3(p2[0], 0, p2[1]))
        pos[2] = pos[2] + height / p3[1] * (-base.camLens.getFov()[0] + 150) / 26.666  # TODO fix fov amendment in zoom

        return pos[0], pos[2]


class HUD(HasFrame):
    def __init__(self):
        HasFrame.__init__(self, 2)

        self.crosshair = OnscreenImage('gui/crosshair.png', pos=(0, 0, 0), scale=0.03, parent=self.frame)
        self.crosshair.setTransparency(1)
        self.crosshair.setColor(1, 1, 1, 0.7)

        # health bar
        # abilities
        # mana pool


class PauseMenu(HasFrame):
    def __init__(self):
        HasFrame.__init__(self, 3)

        button = loader.loadModel('gui/pause-button')

        self.frame['text'] = 'Pause'
        self.frame['text_pos'] = 0, 0.38
        self.frame['text_fg'] = 1, 1, 1, 1
        self.frame['text_scale'] = 0.08
        self.frame['frameColor'] = 0, 0, 0, 0.6
        self.frame['frameSize'] = -.33, .33, -0.5, 0.5
        self.frame.hide()

        pos = .25
        for text, cmd in {
                'Resume': (base.messenger.send, ['Overlay-None']),
                'Options': (base.messenger.send, ['Overlay-Options']),
                'Main menu': (base.messenger.send, ['Menu']),
                'Exit to desktop': (base.messenger.send, ['Exit'])}.items():
            DirectButton(
                parent=self.frame,
                text=text,
                pos=(0, 0, pos),
                relief=DGG.FLAT,
                geom=(button.find('**/button'), button.find('**/button-click'),
                      button.find('**/button-hover'), button.find('**/button-disabled')),
                frameSize=(-0.5, 0.5, -.15, .15),
                text_fg=(1, 1, 1, 1),
                text_scale=0.1,
                text_pos=(0, -0.02),
                scale=0.5,
                rolloverSound=None,
                clickSound=None,
                command=cmd[0],
                extraArgs=cmd[1],
            )
            pos -= .20


class OptionsMenu(HasFrame):
    def __init__(self):
        HasFrame.__init__(self, 4)

        self.changed = {}
        self.items = {}

        self.frame.hide()
        self.frame['frameTexture'] = clamp_texture('gui/bg.jpg')
        self.frame['frameSize'] = base.a2dLeft, base.a2dRight, -1, 1

        for text, cmd, args, pos, align in [
                ('Restore defaults', self.reset_opts, [], (base.a2dRight - .45, 0, -.92), 1),
                ('Apply', self.save_opts, [], (base.a2dRight - .22, 0, -.92), 1),
                ('Back', base.messenger.send, ['Options-Back'], (base.a2dRight - .05, 0, -.92), 1)
        ]:
            DirectButton(
                text=text,
                scale=0.05,
                pos=pos,
                text_align=align,
                text0_fg=(0, 0, 0, 1),
                text1_fg=(.6, .6, .6, 1),
                text2_fg=(.6, .6, .6, 1),
                command=cmd,
                extraArgs=args,
                rolloverSound=None,
                clickSound=None,
                relief=None,
                parent=self.frame
            )

        items = Options.menu_items()
        offset = .1
        height = len(items) * offset / 2

        canvas = ScrollableFrame(canvasSize=(-.75, .75, -height - offset / 2, height), frameSize=(-.8, .8, -.95, .95),
                                 scrollBarWidth=.02, parent=self.frame, frameColor=(0, 0, 0, 0)).canvas

        pos_z = height - offset * .75
        for item in items:
            scale = .05
            color = (1, 1, 1, 1)
            if item['type'] == 'label':
                scale = .08
                color = (0, 0, 0, 1)

            if item['type'] != 'label' and item['type'] != 'separator':
                DirectFrame(
                    frameColor=(0, 0, 0, .3), frameSize=(-.8, .22, -.045, .045), pos=(0, 0, pos_z), parent=canvas
                )

            if item['type'] != 'separator':
                DirectLabel(
                    text=item['title'], text_fg=color, pos=(-.7, 0, pos_z-offset/5), scale=scale,
                    text_align=0, frameColor=(0, 0, 0, 0), parent=canvas
                )

            try:
                self.items[item['name']] = self.make_control(item, canvas, pos_z, offset)
            except KeyError:
                pass

            pos_z -= offset

    def make_control(self, item, canvas, pos_z, offset):
        control = None

        if item['type'] == 'options':

            control = DirectOptionMenu(
                scale=0.07, items=item['items'], initialitem=item['items'].index(item['value']),
                highlightColor=(.65, .65, .65, 1), pos=(0.3, 0, pos_z - offset / 5), parent=canvas,
                command=self.change, extraArgs=[item['name']], popupMarker_pos=(2, 1, 2)
            )

        elif item['type'] == 'check':

            control = DirectCheckButton(
                scale=.04, pos=(.58, 0, pos_z), parent=canvas, indicatorValue=item['value'],
                command=self.change, extraArgs=[item['name']], boxRelief=DGG.FLAT, relief=DGG.FLAT,
                boxImage=('gui/checkbox-disabled.png', 'gui/checkbox-enabled.png', None)
            )
            control.setTransparency(1)

        elif item['type'] == 'slider':

            control = DirectSlider(
                range=item['range'], value=float(item['value']), pageSize=5, parent=canvas,
                frameSize=(-.27, .27, -.04, .04), pos=(.526, 0, pos_z), command=self.change_slider
            )
            control['extraArgs'] = [control, item['name']]

        elif item['type'] == 'key':

            control = DirectButton(
                text=item['value'], text_scale=0.06, text_pos=(0, -.015), pos=(.526, 0, pos_z),
                command=self.change_key_start, rolloverSound=None, clickSound=None, relief=DGG.FLAT,
                parent=canvas, frameSize=(-.27, .27, -.04, .04)
            )
            control['extraArgs'] = [control, item['name']]

        return control

    def reset_opts(self):
        for name, control in self.items.items():
            if type(control) is DirectOptionMenu:
                control.set(control['items'].index(Options.default(name)))
            elif type(control) is DirectCheckButton:
                control['indicatorValue'] = Options.default(name)
                control.setIndicatorValue()
            elif type(control) is DirectSlider:
                control['value'] = Options.default(name)
            elif type(control) is DirectButton:
                control['text'] = Options.default(name)

            self.changed[name] = Options.default(name)

    def save_opts(self):
        for name, val in self.changed.items():
            Options.update(name, val)

        Options.apply()
        Options.save()
        base.messenger.send('Options-Back')

    def change(self, val, name):
        self.changed[name] = val

    def change_slider(self, control, name):
        self.changed[name] = int(control['value'])

    def change_key_start(self, control, name):
        dialog = DirectFrame(
            text='Press any key now or ESC to cancel',
            text_scale=.08,
            sortOrder=100,
            parent=self.frame,
            frameSize=(base.a2dLeft, base.a2dRight, -.3, .3),
            frameColor=(0, 0, 0, .9),
            text_fg=(1, 1, 1, 1),
            suppressKeys=True
        )

        base.acceptOnce('Any-key-pressed', self.change_key, [control, name, dialog])

    def change_key(self, control, name, dialog, key):
        if key != 'escape':
            control['text'] = key
            self.changed[name] = key
        dialog.removeNode()


class ScrollableFrame:
    def __init__(self, horizontal=False, **kwargs):
        self.horizontal = horizontal
        self.frame = DirectScrolledFrame(**kwargs)
        self.canvas = self.frame.getCanvas()
        self.__canvas_parent = self.canvas.getParent()

        base.win.getEngine().renderFrame()
        self.__canvas_start_pos = self.canvas.getPos()

        self.frame['horizontalScroll_value'] = self.frame['verticalScroll_value'] = 1
        self.frame.guiItem.recompute()
        self.__canvas_range = self.__canvas_start_pos - self.canvas.getPos()
        self.__canvas_range[0], self.__canvas_range[2] = abs(self.__canvas_range[0]), abs(self.__canvas_range[2])
        self.frame['horizontalScroll_value'] = self.frame['verticalScroll_value'] = 0

        base.accept('mouse1', self.start_drag)
        base.accept('wheel_up', self.scroll_up, [.2])
        base.accept('wheel_down', self.scroll_down, [.2])

    def start_drag(self):
        if not self.is_hovered():
            return

        m = base.mouseWatcherNode.getMouse()
        m = self.__canvas_parent.getRelativePoint(render2d, Point3(m[0], 0, m[1]))
        task = base.taskMgr.add(self.drag, 'scroll options')
        task.start_mouse = m
        task.canvas_orig_pos = self.canvas.getPos() - self.__canvas_start_pos
        base.accept('mouse1-up', base.taskMgr.remove, [task])

    def drag(self, task):
        m = base.mouseWatcherNode.getMouse()
        m = self.__canvas_parent.getRelativePoint(render2d, Point3(m[0], 0, m[1]))
        canvas_pos = task.canvas_orig_pos + (m - task.start_mouse)

        if self.horizontal:
            self.frame['horizontalScroll_value'] = -canvas_pos[0] / self.__canvas_range[0]

        self.frame['verticalScroll_value'] = canvas_pos[2] / self.__canvas_range[2]

        return task.cont

    def scroll_up(self, length):
        if not self.is_hovered():
            return

        self.frame['verticalScroll_value'] = self.frame['verticalScroll_value'] - length

    def scroll_down(self, length):
        if not self.is_hovered():
            return

        self.frame['verticalScroll_value'] = self.frame['verticalScroll_value'] + length

    def is_hovered(self):
        m = base.mouseWatcherNode.getMouse()
        m = self.__canvas_parent.getRelativePoint(render2d, Point3(m[0], 0, m[1]))
        fs = self.frame['frameSize']

        return fs[0] < m[0] < fs[1] and fs[2] < m[2] < fs[3]


class Loading(HasFrame):
    def __init__(self):
        HasFrame.__init__(self, 5)

        self.frame.hide()
        self.frame['text'] = 'Loading...'
        self.frame['text_fg'] = 1, 1, 1, 1
        self.frame['text_scale'] = .09
        self.frame['frameColor'] = 0, 0, 0, 1
        self.frame['frameSize'] = base.a2dLeft, base.a2dRight, -1, 1

        base.accept('Loading', self.show)
        base.accept('Loaded', self.hide)


class MainMenu(HasFrame):
    def __init__(self):
        HasFrame.__init__(self, 1)

        self.frame['frameSize'] = -.4, .4, -1, 1
        self.frame['frameTexture'] = clamp_texture('gui/menu-frame.png')
        self.frame.setPos(base.a2dLeft+.4, 0, 0)
        self.frame.setTransparency(1)

        logo = OnscreenImage(image='gui/logo.png', pos=(0, 0, .75), scale=(.30, 1, .15), parent=self.frame)
        logo.setTransparency(1)

        button = loader.loadModel('gui/menu-button')
        clamp_texture(('gui/menu-button-hover.png', 'gui/menu-button-click.png'))
        geom = (
            button.find('**/button'),
            button.find('**/button-click'),
            button.find('**/button-hover'),
            button.find('**/button-disabled')
        )

        pos = .0
        for cmd, text in {'Menu-Play': 'Play', 'Menu-Training': 'Training', 'Menu-Heroes': 'Heroes',
                          'Menu-Options': 'Options', 'Exit': 'Exit'}.items():
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
                extraArgs=[cmd],
                rolloverSound=None,
                clickSound=None,
                relief=None,
                geom=geom,
                frameSize=(-.1, 1, -.1, .1),
                parent=self.frame
            )
            pos -= .1


class GameModesMenu(HasFrame):
    def __init__(self):
        HasFrame.__init__(self, 1)

        self.frame['frameTexture'] = clamp_texture('gui/bg.jpg')
        self.frame['frameSize'] = base.a2dLeft, base.a2dRight, -1, 1
        self.frame.hide()

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
            parent=self.frame
        )

        pos = base.a2dRight / 4
        for cmd, text in {'Arcade': 'Arcade', 'Hardcore': 'Hardcore',
                          'Coop': 'Coop', 'Versus': 'Versus'}.items():
            DirectButton(
                text=text,
                text_scale=0.07,
                frameSize=(-.32, .32, -.08, .88),
                pos=(base.a2dLeft + pos, 0, -.3),
                command=base.messenger.send,
                extraArgs=['Play-' + cmd],
                rolloverSound=None,
                clickSound=None,
                relief=DGG.FLAT,
                parent=self.frame
            )
            pos += base.a2dRight / 2
