from PySide import QtCore, QtGui

import FreeCAD as App
import FreeCADGui as Gui

import Draft

from DraftTrackers import Tracker

from DraftTools import redraw3DView

from pivy import coin

class EditTracker(Tracker):
    """
    A custom edit tracker
    """

    def __init__(self, pos, object_name, node_name, marker_type, marker_size):

        self.pos = pos
        self.name = node_name

        self.inactive = False

        self.color = coin.SoBaseColor()

        self.marker = coin.SoMarkerSet()

        self.marker.markerIndex = Gui.getMarkerIndex(marker_type, marker_size)

        self.coords = coin.SoCoordinate3()
        self.coords.point.setValue((pos.x, pos.y, pos.z))

        selnode = None

        if self.inactive:
            selnode = coin.SoSeparator()

        else:
            selnode = coin.SoType.fromName("SoFCSelection").createInstance()
            selnode.documentName.setValue(App.ActiveDocument.Name)
            selnode.objectName.setValue(object_name)
            selnode.subElementName.setValue(node_name)

        node = coin.SoAnnotation()

        selnode.addChild(self.coords)
        selnode.addChild(self.color)
        selnode.addChild(self.marker)

        node.addChild(selnode)

        ontop = not self.inactive

        Tracker.__init__(
            self, children=[node], ontop=ontop, name="EditTracker")

        self.on()

def test_markers():

    App.newDocument('MarkerTest')
    App.setActiveDocument('MarkerTest')
    App.ActiveDocument = App.getDocument('MarkerTest')
    Gui.ActiveDocument = Gui.getDocument('MarkerTest')
    Gui.activeDocument().activeView().viewDefaultOrientation()

    markers1 = ['square', 'cross', 'plus', 'empty', 'quad', 'circle', 'default', 'squarecircle']
    markers2 = ['DIAMOND_FILLED', 'CROSS', 'PLUS', 'SQUARE_LINE', 'SQUARE_FILLED', 'CIRCLE_LINE', 'CIRCLE_FILLED', 'CROSSDIAMOND_LINE']

    pl = App.Placement()
    pl.Base = App.Vector(800.0, 200.0, 0.0)
    Draft.makeRectangle(length=1700, height=-1100, placement = pl, face=False)

    _y = 0.0

    for marker in markers1:
        _x = 1000.0

        for size in [5,7,9,11]:
            EditTracker(App.Vector(_x, _y, 0.0), 'Rectangle', marker + '_' + str(size), marker, size)

            _x += 100

        _y -= 100

    _y = 0.0

    for marker in markers2:
        _x = 2000.0

        for size in [5,7,9,11]:
            EditTracker(App.Vector(_x, _y, 0.0), 'Line', marker + '_' + str(size), marker, size)

            _x += 100

        _y -= 100

    App.ActiveDocument.recompute()
    Gui.SendMsgToActiveView('ViewFit')

test_markers()
