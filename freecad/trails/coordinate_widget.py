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
from freecad.trails import ICONPATH
from PySide2.QtWidgets import QLineEdit
import copy


class CoordinateWidget(QLineEdit):
    """
    Command to show/hide coordinate widget
    """

    def __init__(self):
        """
        Constructor
        """
        mw = FreeCADGui.getMainWindow()
        super(CoordinateWidget, self).__init__(mw)
        mw.statusBar().addPermanentWidget(self)

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return {
            'Pixmap': ICONPATH + '/icons/GeoOrigin.svg',
            'MenuText': "Coordinate Widget",
            'ToolTip': "Show/Hide Geographic Coordinate Widget."
            }

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            self.view = FreeCADGui.ActiveDocument.ActiveView
            self.event_callback = self.view.addEventCallback("SoLocation2Event",self.track_position)
            self.show()
            return True

        try:self.view.removeEventCallback("SoLocation2Event",self.event_callback)
        except Exception: pass
        self.hide()
        return False

    def Activated(self):
        """
        Command activation method
        """
        pass

    def track_position(self, info):
        try:
            obj = self.view.getObjectInfo(self.view.getCursorPos())
            curpos = FreeCAD.Vector(obj["x"], obj["y"], obj["z"])

        except Exception:
            pos = info["Position"]
            curpos = self.view.getPoint(pos)

        org = FreeCAD.ActiveDocument.getObject("GeoOrigin")
        if org:
            base = copy.deepcopy(org.Origin)
            base.z =0
            curpos = base.add(curpos)

        infoText =str(round(curpos[0]/1000,3)) + \
            ", " + str(round(curpos[1]/1000,3)) + \
            ", " + str(round(curpos[2]/1000,3))

        self.setText(infoText)
        self.setMinimumWidth(200)
        self.setMaximumWidth(201)

FreeCADGui.addCommand('Coordinate Widget', CoordinateWidget())
