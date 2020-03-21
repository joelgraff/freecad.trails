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
import MeshPart
import Draft
import os


class CreateSections:

    def __init__(self):
        # Command to create sections for every selected surfaces.
        self.Path = os.path.dirname(__file__)

        self.Resources = {
            'Pixmap': self.Path + '/../Resources/Icons/CreateSections.svg',
            'MenuText': "Create Sections",
            'ToolTip': "Create Sections"
        }

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
        except:
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
        except:
            self.Surfaces = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Surfaces')
            self.Surfaces.Label = "Surfaces"

        SurfacesGroup = self.Surfaces.Group
        self.SurfacesList = []

        for group in SurfacesGroup:
            if group.TypeId == 'Mesh::Feature':
                self.SurfacesList.append(group.Name)
                self.IPFui.SelectSurfacesLW.addItem(group.Label)

    def CreateSections(self):
        FreeCADVersion = FreeCAD.Version()
        if FreeCADVersion[0] == '0' and int(FreeCADVersion[1]) < 19:
            FreeCAD.Console.PrintError(
                "This feature is only available on versions > 0.18")
            return

        try:
            self.SectionsGroup = FreeCAD.ActiveDocument.Sections
        except:
            self.SectionsGroup = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Sections')
            self.SectionsGroup.Label = "Sections"

        GuideLineIndex = self.IPFui.GLGCB.currentIndex()

        if GuideLineIndex < 0:
            FreeCAD.Console.PrintMessage(
                "No Guide Lines Group")
            return

        GuideLineName = self.GuideLinesList[GuideLineIndex]
        GuideLine = FreeCAD.ActiveDocument.getObject(GuideLineName).Group

        # GuideLinesGroup = FreeCAD.ActiveDocument.GuideLines.Group
        CopyMesh = FreeCAD.ActiveDocument.Surface.Mesh.copy()
        Base = CopyMesh.Placement.Base
        CopyMesh.Placement.move(Base.negative())

        for Wire in GuideLine:
            CopyShape = Wire.Shape.copy()
            CopyShape.Placement.move(Base.negative())

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
            Pwire = Draft.makeWire(Section)
            Pwire.Placement.move(Base)
            self.SectionsGroup.addObject(Pwire)

        FreeCAD.ActiveDocument.recompute()


FreeCADGui.addCommand('Create Sections', CreateSections())
