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

import os
import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui
from freecad.trails import ICONPATH
from . import gl_clusters, gl_cluster


class CreateGuideLines:

    def __init__(self):
        """
        Command to create guide lines for selected alignment.
        """
        self.Path = os.path.dirname(__file__)

        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreateGuideLines.ui")
        self.CPGui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreateGuideLinesGroup.ui")

        # Set ui functions
        self.IPFui.CreateB.clicked.connect(self.CreateGuideLines)
        self.IPFui.CancelB.clicked.connect(self.IPFui.close)
        self.IPFui.AddGLGroupB.clicked.connect(self.LoadCGLGui)
        self.CPGui.OkB.clicked.connect(self.CreateNewGroup)
        self.CPGui.CancelB.clicked.connect(self.CPGui.close)
        self.IPFui.AlignmentCB.currentIndexChanged.connect(
            self.ListGuideLinesGroups)

    def GetResources(self):
        # Return the command resources dictionary
        return {
            'Pixmap': ICONPATH + '/icons/CreateGuideLines.svg',
            'MenuText': "Create Guide Lines",
            'ToolTip': "Create guide lines for selected alignment"
            }

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            return True
        return False

    def Activated(self):

        clusters = gl_clusters.get()
        alignments = FreeCAD.ActiveDocument.getObject('Alignments')
        alignment_group = FreeCAD.ActiveDocument.getObject('AlignmentGroup')
        if alignments: alignment_group = alignments

        self.IPFui.setParent(FreeCADGui.getMainWindow())
        self.IPFui.setWindowFlags(QtCore.Qt.Window)
        self.IPFui.show()

        # List Alignments
        self.IPFui.AlignmentCB.clear()
        self.alignment_dict = {}

        for child in alignment_group.Group:
            if child.TypeId == 'Part::Part2DObjectPython':
                self.alignment_dict[child.Label] = child
                self.IPFui.AlignmentCB.addItem(child.Label)

        # Check that the Alignments Group has Wire objects
        if len(self.alignment_dict) == 0:
            FreeCAD.Console.PrintMessage(
                "Please add a Wire Object to the Alignment Group")
            return

        self.ListGuideLinesGroups()

    def ListGuideLinesGroups(self):

        # List Guide Lines Groups.
        self.IPFui.GLGroupCB.clear()
        clusters = gl_clusters.get()
        self.glc_dict = {}

        for child in clusters.Group:
            if child.Proxy.Type == 'Trails::GLCluster':
                self.glc_dict[child.Label] = child
                self.IPFui.GLGroupCB.addItem(child.Label)

    def LoadCGLGui(self):

        # Load Create Guide Lines Group UI
        self.CPGui.setParent(self.IPFui)
        self.CPGui.setWindowFlags(QtCore.Qt.Window)
        self.CPGui.show()

    def CreateNewGroup(self):
        # Target alignment
        text_alignment = self.IPFui.AlignmentCB.currentText()

        if not text_alignment:
            FreeCAD.Console.PrintMessage(
                "Please add a Alignment object to the Alignment Group")
            return None, 0.0, 0.0

        alignment = self.alignment_dict[text_alignment]

        # Create new guide lines group
        cluster_name = self.CPGui.GuideLinesGroupNameLE.text()
        new_cluster = gl_cluster.create(alignment, cluster_name)

        self.glc_dict[new_cluster.Label] = new_cluster
        self.IPFui.GLGroupCB.addItem(new_cluster.Label)
        self.CPGui.close()

    def CreateGuideLines(self):
        """
        Generates guidelines along a selected alignment
        """
        # Target cluster
        text_cluster = self.IPFui.GLGroupCB.currentText()

        if not text_cluster:
            FreeCAD.Console.PrintMessage(
                "Please add a Guide Line Group")
            return

        cluster = self.glc_dict[text_cluster]


FreeCADGui.addCommand('Create Guide Lines', CreateGuideLines())
