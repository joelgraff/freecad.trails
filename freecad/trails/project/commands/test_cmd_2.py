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

import WorkingPlane

from PySide import QtCore, QtGui

import FreeCAD as App
import FreeCADGui as Gui

import Draft
import DraftGeomUtils
import DraftVecUtils

from DraftTrackers import editTracker
from DraftTools import Modifier
from DraftTools import selectObject, getPoint, redraw3DView

#from .edit_tracker import editTracker

plane = WorkingPlane.plane()

class Command2(Modifier):
    "The Draft_Edit FreeCAD command definition"

    def __init__(self):
        self.running = False
        self.trackers = []
        self.obj = None
        self.call = None
        self.selectstate = None
        self.originalDisplayMode = None
        self.originalPoints = None
        self.originalNodes = None

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Edit',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Edit", "Edit"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Edit", "Edits the active object")}

    def Activated(self):

        Modifier.Activated(self,"Edit")

        #get the selection, and proceed
        #if Gui.Selection.getSelection():

        self.selection = Gui.Selection.getSelection()
        self.proceed()
 

    def proceed(self):

        #remove the callback...?
       #if self.call:
       #     self.view.removeEventCallback("SoEvent", self.call)
       #     self.call = None

        self.obj = Gui.Selection.getSelection()


        self.obj = self.obj[0]

        self.editing = None
        self.editpoints = []
        self.pl = None
        self.arc3Pt = False

        for p in self.obj.Points:
            self.editpoints.append(p)

        self.trackers.append(editTracker(App.Vector(1,1,0), self.obj.Name, 0))

        for ep in range(len(self.editpoints)):
            self.trackers.append(editTracker(self.editpoints[ep],self.obj.Name,ep))

###############################################################################
    def finish(self,closed=False):
        "terminates the operation"
        Gui.Snapper.setSelectMode(False)
        if self.obj and closed:
            if "Closed" in self.obj.PropertiesList:
                if not self.obj.Closed:
                    self.obj.Closed = True
        if self.ui:
            if self.trackers:
                for t in self.trackers:
                    t.finalize()
        if self.obj:
            if hasattr(self.obj.ViewObject,"Selectable") and (self.selectstate != None):
                self.obj.ViewObject.Selectable = self.selectstate
        if Draft.getType(self.obj) == "Structure":
            if self.originalDisplayMode != None:
                self.obj.ViewObject.DisplayMode = self.originalDisplayMode
            if self.originalPoints != None:
                self.obj.ViewObject.NodeSize = self.originalPoints
            if self.originalNodes != None:
                self.obj.ViewObject.ShowNodes = self.originalNodes
        self.selectstate = None
        self.originalDisplayMode = None
        self.originalPoints = None
        self.originalNodes = None
        Modifier.finish(self)
        plane.restore()
        if Gui.Snapper.grid:
            Gui.Snapper.grid.set()
        self.running = False

###############################################################################
    def action(self,arg):
        "scene event handler"

        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
            elif arg["Key"] == "f":
                self.finish()
            elif arg["Key"] == "c":
                self.finish(closed=True)

        elif arg["Type"] == "SoLocation2Event": #mouse movement detection
            self.point,ctrlPoint,info = getPoint(self,arg)
            if self.editing != None:
                self.trackers[self.editing].set(self.point)
                # commented out the following line to disable updating
                # the object during edit, otherwise it confuses the snapper
                #self.update(self.trackers[self.editing].get())
            if hasattr(self.obj.ViewObject,"Selectable"):
                if self.ui.addButton.isChecked():
                    self.obj.ViewObject.Selectable = True
                else:
                    self.obj.ViewObject.Selectable = False
            redraw3DView()

        elif arg["Type"] == "SoMouseButtonEvent":

            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                self.ui.redraw()

                if self.editing == None:
                    p = Gui.ActiveDocument.ActiveView.getCursorPos()
                    done = False
                    selobjs = Gui.ActiveDocument.ActiveView.getObjectsInfo(p)
                    if not selobjs:
                        return
                    for info in selobjs:
                        if info["Object"] == self.obj.Name:
                            if done:
                                return

                        ep = None
                        if ('EditNode' in info["Component"]):
                            ep = int(info["Component"][8:])
                        elif ('Vertex' in info["Component"]) or ('Edge' in info["Component"]):
                            p = App.Vector(info["x"],info["y"],info["z"])
                            for i,t in enumerate(self.trackers):
                                if (t.get().sub(p)).Length <= 0.01:
                                    ep = i
                                    break
                        if ep != None:

                            self.arc3Pt = False # decide if it's deselected after every editing point
                            self.ui.pointUi()
                            self.ui.isRelative.show()
                            self.editing = ep
                            self.trackers[self.editing].off()
                            if hasattr(self.obj.ViewObject,"Selectable"):
                                self.obj.ViewObject.Selectable = False
                            self.node.append(self.trackers[self.editing].get())
                            Gui.Snapper.setSelectMode(False)
                            done = True
                else:
                    self.trackers[self.editing].on()
                    #if hasattr(self.obj.ViewObject,"Selectable"):
                    #    self.obj.ViewObject.Selectable = True
                    Gui.Snapper.setSelectMode(True)
                    self.numericInput(self.trackers[self.editing].get())

    def update(self,v):
        self.doc.openTransaction("Edit")

        pts = self.obj.Points
        editPnt = self.invpl.multVec(v)
        # DNC: allows to close the curve by placing ends close to each other
        tol = 0.001
        if ( ( self.editing == 0 ) and ( (editPnt - pts[-1]).Length < tol) ) or ( self.editing == len(pts) - 1 ) and ( (editPnt - pts[0]).Length < tol):
            self.obj.Closed = True
        # DNC: fix error message if edited point coincides with one of the existing points
        if ( editPnt in pts ) == False:

            # check that the new point lies on the plane of the wire
            import DraftGeomUtils
            if self.obj.Closed:
                n = DraftGeomUtils.getNormal(self.obj.Shape)
                dv = editPnt.sub(pts[self.editing])
                rn = DraftVecUtils.project(dv,n)
                if dv.Length:
                    editPnt = editPnt.add(rn.negative())
            pts[self.editing] = editPnt
            self.obj.Points = pts
            self.trackers[self.editing].set(v)

        self.doc.commitTransaction()
        try:
            Gui.ActiveDocument.ActiveView.redraw()
        except AttributeError as err:
            pass

    def numericInput(self,v,numy=None,numz=None):
        '''this function gets called by the toolbar
        when valid x, y, and z have been entered there'''
        if (numy != None):
            v = App.Vector(v,numy,numz)
        self.update(v)
        self.doc.recompute()
        self.editing = None
        self.ui.editUi(self.ui.lastMode)
        self.node = []

    def resetTrackers(self):
        for t in self.trackers:
            t.finalize()
        self.trackers = []

        for ep in range(len(self.obj.Points)):
            objPoints = self.obj.Points[ep]
            if self.pl: objPoints = self.pl.multVec(objPoints)
            self.trackers.append(editTracker(objPoints,self.obj.Name,ep,self.obj.ViewObject.LineColor))

Gui.addCommand('Command2', Command2())
