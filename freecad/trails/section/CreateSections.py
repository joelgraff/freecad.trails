# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui
from freecad.trails import ICONPATH
import MeshPart
import Draft
import os


view = FreeCADGui.ActiveDocument.ActiveView

class CreateSections:

    def __init__(self):

        self.Resources = {
            'Pixmap': ICONPATH + '/icons/CreateSections.svg',
            'MenuText': "Create Sections",
            'ToolTip': "Create Sections"
        }

        # Command to create sections for every selected surfaces.
        self.Path = os.path.dirname(__file__)

        # Import *.ui file(s)
        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreateSections.ui")

        # To Do List
        self.IPFui.CreateB.clicked.connect(self.CreateSections)
        self.IPFui.CancelB.clicked.connect(self.IPFui.close)

    def GetResources(self):
        # Return the command resources dictionary
        return self.Resources

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        return True

    def Activated(self):
        self.IPFui.setParent(FreeCADGui.getMainWindow())
        self.IPFui.setWindowFlags(QtCore.Qt.Window)
        self.IPFui.show()

        self.IPFui.GLGCB.clear()

        try:
            self.GuideLines = FreeCAD.ActiveDocument.GuideLines
        except Exception:
            self.GuideLines = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'GuideLines')
            self.GuideLines.Label = "Guide Lines"

        GuideLinesGroup = self.GuideLines.Group
        self.GuideLinesList = []

        for group in GuideLinesGroup:
            if group.TypeId == 'App::DocumentObjectGroup':
                self.GuideLinesList.append(group.Name)
                self.IPFui.GLGCB.addItem(group.Label)

        self.IPFui.SelectSurfacesLW.clear()
        try:
            self.Surfaces = FreeCAD.ActiveDocument.Surfaces
        except Exception:
            self.Surfaces = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Surfaces')
            self.Surfaces.Label = "Surfaces"

        SurfacesGroup = self.Surfaces.Group
        self.SurfacesList = {}

        for surface in SurfacesGroup:
            if surface.TypeId == 'Mesh::Feature':
                self.SurfacesList[surface.Label] = surface
                self.IPFui.SelectSurfacesLW.addItem(surface.Label)

    @staticmethod
    def convert2View(Section, origin):
        import math
        sectionView = []
        if origin: Section.insert(0, origin)
        sectionView.append(FreeCAD.Vector(0, 0, 0))
        for i in range(0, len(Section)-1):
            point = Section[i]
            pointNext = Section[i+1]
            pointVirt = FreeCAD.Vector(pointNext.x, pointNext.y, point.z)
            vecReal = point.sub(pointNext)
            vecVir = point.sub(pointVirt)
            length = vecReal.Length
            angle = vecVir.getAngle(vecReal)
            dx = length * math.cos(angle)
            dy = length * math.sin(angle)
            if vecVir.z - vecReal.z < 0: dy = -dy
            sectionView.append(sectionView[-1].add(FreeCAD.Vector(dx, dy, 0)))
        sectionView.pop(0)
        return sectionView

    def placeSecViews(self, event):
        """
        Select section views location
        """
        try:
            if (event["Button"] == "BUTTON1") and (event["State"] == "DOWN"):
                clickPos = event["Position"]
                view.removeEventCallback("SoEvent", self.callback)
                position = view.getPoint(clickPos)
                self.drawSecViews(position)
        except Exception: pass


    def CreateSections(self):
        FreeCADVersion = FreeCAD.Version()
        if FreeCADVersion[0] == '0' and int(FreeCADVersion[1]) < 19:
            FreeCAD.Console.PrintError(
                "This feature is only available on versions > 0.18")
            return

        try:
            self.SectionsGroup = FreeCAD.ActiveDocument.Sections
        except Exception:
            self.SectionsGroup = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Sections')
            self.SectionsGroup.Label = "Sections"

        self.GuideLineIndex = self.IPFui.GLGCB.currentIndex()

        if self.GuideLineIndex < 0:
            FreeCAD.Console.PrintMessage(
                "No Guide Lines Group")
            return

        self.callback = view.addEventCallback("SoEvent",self.placeSecViews)

    def drawSecViews(self, position):
        GuideLineName = self.GuideLinesList[self.GuideLineIndex]
        GuideLine = FreeCAD.ActiveDocument.getObject(GuideLineName).Group
        for Wire in GuideLine:
            CopyShape = Wire.Shape.copy()
            origin = None
            for SelectedItem in self.IPFui.SelectSurfacesLW.selectedItems():
                Surface = self.SurfacesList[SelectedItem.text()]
                CopyMesh = Surface.Mesh.copy()

                Param1 = MeshPart.findSectionParameters(
                    CopyShape.Edge1, CopyMesh, FreeCAD.Vector(0, 0, 1))
                Param1.insert(0, CopyShape.Edge1.FirstParameter+1)
                Param1.append(CopyShape.Edge1.LastParameter-1)

                Param2 = MeshPart.findSectionParameters(
                    CopyShape.Edge2, CopyMesh, FreeCAD.Vector(0, 0, 1))
                Param2.insert(0, CopyShape.Edge2.FirstParameter+1)
                Param2.append(CopyShape.Edge2.LastParameter-1)

                Points1 = [CopyShape.Edge1.valueAt(i) for i in Param1]
                Points2 = [CopyShape.Edge2.valueAt(i) for i in Param2]

                Section = MeshPart.projectPointsOnMesh(
                    Points1+Points2, CopyMesh, FreeCAD.Vector(0, 0, 1))
                sectionView = self.convert2View(Section, origin)
                Pwire = Draft.makeWire(sectionView)
                Pwire.Placement.move(position)
                self.SectionsGroup.addObject(Pwire)
                origin = Section[0]
            origin = None
            position = position.add(FreeCAD.Vector(110000, 0, 0))
        FreeCAD.ActiveDocument.recompute()
FreeCADGui.addCommand('Create Sections', CreateSections())
