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
from . import surface
from ..point import point_groups
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
        # Create Point_Groups' groups
        PointGroups = point_groups.get()

        # Set and show UI
        self.IPFui.setParent(FreeCADGui.getMainWindow())
        self.IPFui.setWindowFlags(QtCore.Qt.Window)
        self.IPFui.show()

        # Create QStandardItemModel to list point groups on QListView
        model = QtGui.QStandardItemModel()
        self.IPFui.PointGroupsLV.setModel(model)

        # Create QStandardItem for every point group
        self.GroupList = []
        for PointGroup in PointGroups.Group:
            self.GroupList.append(PointGroup.Name)
            SubGroupName = PointGroup.Label
            item = QtGui.QStandardItem(SubGroupName)
            model.appendRow(item)

    def CreateSurface(self):
        """
        Create Surface by using point groups.
        """
        # Print warning if there isn't selected group
        if len(self.IPFui.PointGroupsLV.selectedIndexes()) < 1:
            FreeCAD.Console.PrintMessage("No Points object selected")
            return

        # Get selected group(s) points
        points = []
        for SelectedIndex in self.IPFui.PointGroupsLV.selectedIndexes():
            Index = self.GroupList[SelectedIndex.row()]
            PointGroup = FreeCAD.ActiveDocument.getObject(Index)
            points.extend(PointGroup.Points)

        SurfaceNameLE = self.IPFui.SurfaceNameLE.text()
        surface.create(points, SurfaceNameLE)
        FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand('Create Surface', CreateSurface())
