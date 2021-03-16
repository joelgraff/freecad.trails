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

import FreeCAD, FreeCADGui
from pivy import coin
from PySide2 import QtCore
from freecad.trails import ICONPATH
from ..surface import surfaces
from . import cross_sections, cross_section
import os

class CreateSections:

    def __init__(self):

        # Command to create sections for every selected surfaces.
        self.Path = os.path.dirname(__file__)

        # Import *.ui file(s)
        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/create_sections.ui")

        # Set button functions
        self.IPFui.CreateB.clicked.connect(self.start_event)
        self.IPFui.CancelB.clicked.connect(self.IPFui.close)

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return {
            'Pixmap': ICONPATH + '/icons/CreateSections.svg',
            'MenuText': "Create Section Views",
            'ToolTip': "Create Section Views"
            }

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            # Check for selected object
            self.selection = FreeCADGui.Selection.getSelection()
            if self.selection:
                if self.selection[-1].Proxy.Type == 'Trails::Guidelines':
                    return True
        return False

    def Activated(self):
        """
        Command activation method
        """
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.IPFui.setParent(FreeCADGui.getMainWindow())
        self.IPFui.setWindowFlags(QtCore.Qt.Window)
        self.IPFui.SelectSurfacesLW.clear()
        self.IPFui.show()

        self.surface_list = {}
        surface_group = surfaces.get()
        for surface in surface_group.Group:
            self.surface_list[surface.Label] = surface
            self.IPFui.SelectSurfacesLW.addItem(surface.Label)

    def start_event(self):
        """
        Start event to detect mouse click
        """
        self.callback = self.view.addEventCallbackPivy(
            coin.SoButtonEvent.getClassTypeId(), self.select_position)

    def select_position(self, event):
        """
        Select section views location
        """
        # Get event
        event = event.getEvent()

        # If mouse left button pressed get picked point
        if event.getTypeId().isDerivedFrom(coin.SoMouseButtonEvent.getClassTypeId()):
            if event.getButton() == coin.SoMouseButtonEvent.BUTTON1 \
                and event.getState() == coin.SoMouseButtonEvent.DOWN:

                # Finish event
                self.view.removeEventCallbackPivy(
                    coin.SoButtonEvent.getClassTypeId(), self.callback)

                pos = event.getPosition().getValue()
                position = self.view.getPoint(pos[0], pos[1])
                position.z = 0

                cluster = self.selection[-1].getParentGroup()

                for item in cluster.Group:
                    if item.Proxy.Type == 'Trails::CrossSections':
                        cs = item
                        cs.Position = position
                        break

                for item in self.IPFui.SelectSurfacesLW.selectedItems():
                    surface = self.surface_list[item.text()]
                    sections = cross_section.create(surface)
                    cs.addObject(sections)

                FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand('Create Sections', CreateSections())
