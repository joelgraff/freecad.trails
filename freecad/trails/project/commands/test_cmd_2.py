# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

import math
import WorkingPlane

from PySide import QtCore, QtGui
from pivy import coin

import FreeCAD  as App
import FreeCADGui as Gui
from FreeCAD import Vector

import Draft
import DraftGeomUtils
import DraftVecUtils

from DraftTrackers import editTracker, Tracker, lineTracker
from DraftTools import Modifier, Creator, DraftTool
from DraftTools import selectObject, getPoint, redraw3DView

#from .edit_tracker import editTracker

plane = WorkingPlane.plane()

class radiusTracker(Tracker):
    "A tracker that displays a transparent sphere to inicate a radius"
    def __init__(self,position=App.Vector(0,0,0),radius=1):
        self.trans = coin.SoTransform()
        self.trans.translation.setValue([position.x,position.y,position.z])
        self.line = coin.SoLineSet()
        self.line.numVertices.setValue(4)
        m = coin.SoMaterial()
        m.transparency.setValue(0.9)
        m.diffuseColor.setValue([0, 1, 0])
        self.coords = coin.SoCoordinate3()
        self.coords.point.set1Value(0, [0.0, 0.0, 0.0])
        self.coords.point.set1Value(1, [100.0, 0.0, 0.0])
        self.coords.point.set1Value(2, [200.0, 200.0, 0.0])
        self.coords.point.set1Value(3, [200.0, 400.0, 0.0])

        Tracker.__init__(self,children=[m, self.trans, self.line, self.coords],name="radiusTracker")

        self.on()

    def update(self,arg1,arg2=None):
        self.trans.translation.setValue([arg1.x,arg1.y,arg1.z])

class Command2(DraftTool):

    "the Draft_Arc FreeCAD command definition"

    def __init__(self):
        DraftTool.__init__(self)

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Arc',
                'Accel' : "A, R",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Arc", "Arc"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Arc", "Creates an arc. CTRL to snap, SHIFT to constrain")}

    def Activated(self):
        DraftTool.Activated(self,"TrackerTest")

        self.event_cb = self.view.addEventCallback("SoEvent", self.action)
        self.tracker = radiusTracker()
        self.tracker.on()

    def finish(self,closed=False,cont=False):
        self.tracker.finalize()
        self.doc.recompute()

    def action(self,arg):
        "scene event handler"
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event":
            _p = Gui.ActiveDocument.ActiveView.getCursorPos()
            _pt = self.view.getPoint(_p)
            self.tracker.update(_pt)
            print(_pt)
            redraw3DView()

        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                pass

Gui.addCommand('Command2', Command2())
