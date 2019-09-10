from pivy import coin

import FreeCADGui as Gui

from DraftGui import todo

class NodeTracker():

    counter = 0

    def __init__(self, coord):

        self.node = coin.SoSeparator()
        self.coordinate = coin.SoCoordinate3()
        self.crosshair_coord = coin.SoCoordinate3()
        self.transform = coin.SoTransform()

        _selection_node = \
            coin.SoType.fromName("SoFCSelection").createInstance()

        _selection_node.documentName.setValue('Document')
        _selection_node.objectName.setValue('Test Tracker')
        _selection_node.subElementName.setValue(
            'NODE-' + str(NodeTracker.counter)
        )

        self.node.addChild(_selection_node)
        self.node.addChild(self.transform)
        self.node.addChild(self.coordinate)
        self.node.addChild(coin.SoMarkerSet())

        self.coordinate.point.setValue(tuple(coord))

        NodeTracker.counter += 1


class TestTracker():

    def __init__(self):

        self.node.addChild(coin.SoLineSet())

        self.coordinate.point.setValues(
            [(200.0, 200.0, 0.0), (100.0, -200.0, 0.0), (0.0, 0.0, 0.0),
            (-300.0, 200.0, 0.0)]
            )

        self.view = Gui.ActiveDocument.ActiveView
        self.view.addEventCallback(
            'SoLocation2Event', self.mouse_event)

        _fn = lambda _x: self.view.getSceneGraph().insertChild(_x, 0)

        self.crosshair = self.create_crosshair()

        todo.delay(_fn, self.node)
        todo.delay(_fn, self.crosshair)

    def create_crosshair(self):

        _switch = coin.SoSwitch()
        _node = coin.SoSeparator()
        _coord = coin.SoCoordinate3()
        _transform = coin.SoTransform()

        self.crosshair_coord.point.setValues(0, 5, [
            (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0),
            (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)
        ])
        _nodes = [_transform, self.crosshair_coord, coin.SoLineSet()]

        for _v in _nodes:
            _node.addChild(_v)

        _switch.addChild(_node)
        _switch.whichChild = -1

        return _switch

    def mouse_event(self, arg):

        pos = self.view.getCursorPos()
        info = self.view.getObjectInfo(pos)
        coord_1 = self.view.getPoint((0, 0))
        coord_2 = self.view.getPoint((100, 0))

        delta = abs(coord_2[0] - coord_1[0])

        _scale = App.ParamGet("User parameter:BaseApp/Preferences/View").GetFloat("PickRadius")

        _scale = abs(_scale - 5.0) / _scale

        delta *= _scale

        self.crosshair_coord.point.setValues(0, 5, [
            (float(delta), 0.0, 0.0), (0.0, float(delta), 0.0),
            (float(-delta), 0.0, 0.0), (0.0, float(-delta), 0.0),
            (float(delta), 0.0, 0.0)
        ])

        if info and info['Component'] == 'NODE-0':
            self.crosshair.whichChild = -3
        else:
            self.crosshair.whichChild = -1
