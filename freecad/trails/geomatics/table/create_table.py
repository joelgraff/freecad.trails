# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Hakan Seven <hakanseven12@gmail.com>             *
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
from . import table
import os

class CreateTable:

    def __init__(self):

        # Command to create sections for every selected surfaces.
        self.path = os.path.dirname(__file__)

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return {
            'Pixmap': ICONPATH + '/icons/table.svg',
            'MenuText': "Create Volume Table",
            'ToolTip': "Create Volume Table"
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
                if self.selection[-1].Proxy.Type == 'Trails::Volume':
                    return True
        return False

    def Activated(self):
        """
        Command activation method
        """
        #Start event to detect mouse click
        self.view = FreeCADGui.ActiveDocument.ActiveView
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

                vol_group = self.selection[-1].getParentGroup()
                cluster = vol_group.getParentGroup()

                for item in cluster.Group:
                    if item.Proxy.Type == 'Trails::Guidelines':
                        gl = item
                    if item.Proxy.Type == 'Trails::Tables':
                        tables = item

                tab = table.create(position, gl, self.selection[-1])
                
                tables.addObject(tab)

                FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand('Create Table', CreateTable())
