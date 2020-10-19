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
from freecad.trails import ICONPATH
from ...project.support import utils
import Mesh
import os


class CreateSurface:
    """
    Command to create a new surface
    """

    def __init__(self):
        """
        Constructor
        """

        # Set icon,  menu text and tooltip
        self.resources = {
            'Pixmap': ICONPATH + '/icons/CreateSurface.svg',
            'MenuText': "Create Surface",
            'ToolTip': "Create surface from selected point group(s)."
            }

        # Get file path
        self.Path = os.path.dirname(__file__)

        # Get *.ui file(s)
        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreateSurface.ui")

        # UI connections
        UI = self.IPFui
        UI.CreateB.clicked.connect(self.CreateSurface)
        UI.CancelB.clicked.connect(UI.close)

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return self.resources

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument is None:
            return False
        return True

    def Activated(self):
        """
        Command activation method
        """
        # Create 'Surfaces' and 'Point_Groups' groups
        try:
            self.Surfaces = FreeCAD.ActiveDocument.Surfaces
        except Exception:
            FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Surfaces')
            self.Surfaces = FreeCAD.ActiveDocument.Surfaces

        try:
            PointGroups = FreeCAD.ActiveDocument.Point_Groups.Group
        except Exception:
            FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Point_Groups')
            PointGroups = FreeCAD.ActiveDocument.Point_Groups.Group
            PointGroups.Label = "Point Groups"

        # Set and show UI
        self.IPFui.setParent(FreeCADGui.getMainWindow())
        self.IPFui.setWindowFlags(QtCore.Qt.Window)
        self.IPFui.show()

        # Create QStandardItemModel to list point groups on QListView
        model = QtGui.QStandardItemModel()
        self.IPFui.PointGroupsLV.setModel(model)

        # Create QStandardItem for every point group
        self.GroupList = []
        for PointGroup in PointGroups:
            self.GroupList.append(PointGroup.Name)
            SubGroupName = PointGroup.Label
            item = QtGui.QStandardItem(SubGroupName)
            model.appendRow(item)

    def MaxLength(self, P1, P2, P3):
        """
        Calculation of the 2D length between triangle edges
        """
        p1 = FreeCAD.Vector(P1[0], P1[1], 0)
        p2 = FreeCAD.Vector(P2[0], P2[1], 0)
        p3 = FreeCAD.Vector(P3[0], P3[1], 0)
        # Get user input
        MaxlengthLE = self.IPFui.MaxlengthLE.text()

        # Calculate length between triangle vertices
        List = [[p1, p2], [p2, p3], [p3, p1]]
        for i, j in List:
            D1 = i.sub(j)

            # Compare with input
            if D1.Length > int(MaxlengthLE)*1000:
                return False
        return True

    def MaxAngle(self, P1, P2, P3):
        """
        Calculation of the 2D angle between triangle edges
        """
        import math
        p1 = FreeCAD.Vector(P1[0], P1[1], 0)
        p2 = FreeCAD.Vector(P2[0], P2[1], 0)
        p3 = FreeCAD.Vector(P3[0], P3[1], 0)

        # Get user input
        MaxAngleLE = self.IPFui.MaxAngleLE.text()

        # Calculate angle between triangle vertices
        List = [[p1, p2, p3], [p2, p3, p1], [p3, p1, p2]]
        for j, k, l in List:
            D1 = j.sub(k)
            D2 = l.sub(k)
            Radian = D1.getAngle(D2)
            Degree = math.degrees(Radian)

            # Compare with input
            if Degree > int(MaxAngleLE):
                return False
        return True

    def CreateSurface(self):
        import numpy as np
        import scipy.spatial

        # Print warning if there isn't selected group
        if len(self.IPFui.PointGroupsLV.selectedIndexes()) < 1:
            FreeCAD.Console.PrintMessage("No Points object selected")
            return

        # Get selected group(s) points
        test = []
        for SelectedIndex in self.IPFui.PointGroupsLV.selectedIndexes():
            Index = self.GroupList[SelectedIndex.row()]
            PointGroup = FreeCAD.ActiveDocument.getObject(Index)

            for Point in PointGroup.Points.Points:
                xx = float(Point.x)
                yy = float(Point.y)
                zz = float(Point.z)
                test.append([xx, yy, zz])

        # Normalize points
        fpoint = test[0]
        base = FreeCAD.Vector(fpoint[0], fpoint[1], fpoint[2])
        nbase = utils.rendering_fix(base)
        data = []
        for i in test:
            data.append([i[0] - nbase.x, i[1] - nbase.y, i[2] - nbase.z])
        Data = np.array(data)

        # Create delaunay triangulation
        tri = scipy.spatial.Delaunay(Data[:, :2])

        MeshList = []

        for i in tri.vertices:
            first = int(i[0])
            second = int(i[1])
            third = int(i[2])

            #Test triangle
            if self.MaxLength(Data[first], Data[second], Data[third])\
                    and self.MaxAngle(Data[first], Data[second], Data[third]):
                MeshList.append(Data[first])
                MeshList.append(Data[second])
                MeshList.append(Data[third])

        MeshObject = Mesh.Mesh(MeshList)
        MeshObject.Placement.move(nbase)
        SurfaceNameLE = self.IPFui.SurfaceNameLE.text()
        Surface = FreeCAD.ActiveDocument.addObject(
            "Mesh::Feature", SurfaceNameLE)
        Surface.Mesh = MeshObject
        Surface.Label = SurfaceNameLE
        self.Surfaces.addObject(Surface)
        FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand('Create Surface', CreateSurface())
