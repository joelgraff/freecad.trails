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
from FreeCAD import Base
from PySide import QtCore, QtGui
import numpy as np
import Mesh
import os


class CreateSurface:
    """
    Command to create a new surface
    """

    def __init__(self):

        self.Path = os.path.dirname(__file__)

        self.resources = {
            'Pixmap': self.Path + '/../Resources/Icons/CreateSurface.svg',
            'MenuText': "Create Surface",
            'ToolTip': "Create surface from selected point group(s)."
            }
        # Import *.ui file(s)
        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreateSurface.ui")

        # To Do List
        UI = self.IPFui
        UI.CreateB.clicked.connect(self.CreateSurface)
        UI.CancelB.clicked.connect(UI.close)

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return self.resources

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        return True

    def Activated(self):
        try:
            self.Surfaces = FreeCAD.ActiveDocument.Surfaces
        except Exception:
            self.Surfaces = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Surfaces')

        try:
            PointGroups = FreeCAD.ActiveDocument.Point_Groups.Group
        except Exception:
            FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Point_Groups')
            PointGroups = FreeCAD.ActiveDocument.Point_Groups.Group
            PointGroups.Label = "Point Groups"

        self.IPFui.setParent(FreeCADGui.getMainWindow())
        self.IPFui.setWindowFlags(QtCore.Qt.Window)
        self.IPFui.show()
        model = QtGui.QStandardItemModel()
        self.IPFui.PointGroupsLV.setModel(model)

        self.GroupList = []

        for PointGroup in PointGroups:
            self.GroupList.append(PointGroup.Name)
            SubGroupName = PointGroup.Label
            item = QtGui.QStandardItem(SubGroupName)
            model.appendRow(item)

    def MaxLength(self, P1, P2, P3):
        MaxlengthLE = self.IPFui.MaxlengthLE.text()
        List = [[P1, P2], [P2, P3], [P3, P1]]
        Result = []
        for i, j in List:
            DeltaX = i[0] - j[0]
            DeltaY = i[1] - j[1]
            Length = (DeltaX**2+DeltaY**2)**0.5
            Result.append(Length)
        if Result[0] <= int(MaxlengthLE)*1000 \
                and Result[1] <= int(MaxlengthLE)*1000 \
                and Result[2] <= int(MaxlengthLE)*1000:
            return True
        else:
            return False

    def MaxAngle(self, P1, P2, P3):
        import math
        MaxAngleLE = self.IPFui.MaxAngleLE.text()
        List = [[P1, P2], [P2, P3], [P3, P1]]
        Result = []
        for i, j in List:
            Radian = FreeCAD.Vector(i).getAngle(FreeCAD.Vector(j))
            Angle = math.degrees(Radian)
            Result.append(Angle)
            
        if Result[0] <= int(MaxAngleLE)*1000 \
                and Result[1] <= int(MaxAngleLE)*1000 \
                and Result[2] <= int(MaxAngleLE)*1000:
            return True
        else:
            return False

    def CreateSurface(self):

        if len(self.IPFui.PointGroupsLV.selectedIndexes()) < 1:
            FreeCAD.Console.PrintMessage("No Points object selected")
            return

        import numpy as np

        Test = []

        # Create a set of points
        for SelectedIndex in self.IPFui.PointGroupsLV.selectedIndexes():
            Index = self.GroupList[SelectedIndex.row()]
            PointGroup = FreeCAD.ActiveDocument.getObject(Index)

            for Point in PointGroup.Points.Points:
                xx = float(Point.x)
                yy = float(Point.y)
                zz = float(Point.z)
                Test.append([xx, yy, zz])

        Data = np.array(Test)
        DataOn = Data.mean(axis=0)
        Basex = FreeCAD.Vector(DataOn[0], DataOn[1], DataOn[2])
        Data -= DataOn

        from .Delaunator import Delaunator

        # Create Delaunay Triangulation
        triangles = Delaunator(Data[:, :2]).triangles

        MeshList = []

        for i in range(0, len(triangles), 3):
            if self.MaxLength(Data[triangles[i]], Data[triangles[i+1]], Data[triangles[i+2]])\
                    and self.MaxAngle(Data[triangles[i]], Data[triangles[i+1]], Data[triangles[i+2]]):
                MeshList.append(Data[triangles[i+2]])
                MeshList.append(Data[triangles[i+1]])
                MeshList.append(Data[triangles[i]])

        #Create Surface
        MeshObject = Mesh.Mesh(MeshList)
        MeshObject.Placement.move(Basex)
        SurfaceNameLE = self.IPFui.SurfaceNameLE.text()
        Surface = FreeCAD.ActiveDocument.addObject(
            "Mesh::Feature", SurfaceNameLE)
        Surface.Mesh = MeshObject
        Surface.Label = SurfaceNameLE
        self.Surfaces.addObject(Surface)
        FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand('Create Surface', CreateSurface())
