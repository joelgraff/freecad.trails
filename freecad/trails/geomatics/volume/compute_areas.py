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

import FreeCAD
import FreeCADGui
from freecad.trails import ICONPATH
from . import volumes, volume


class ComputeAreas:
    """
    Command to compute areas between surface sections
    """

    def __init__(self):
        """
        Command to create guide lines for selected alignment.
        """
        pass

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return {
            'Pixmap': ICONPATH + '/icons/volume.svg',
            'MenuText': "Compute areas",
            'ToolTip': "Compute areas between surface sections"
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
        """
        Command activation method
        """
        # Check for selected object
        selection = FreeCADGui.Selection.getSelection()
        cs = selection[-1].getParentGroup()
        region = cs.getParentGroup()

        for item in region.Group:
            if item.Proxy.Type == 'Trails::Volumes':
                vol = item
                break

        vol_areas = volume.create(selection)
        vol.addObject(vol_areas)


FreeCADGui.addCommand('Compute Areas', ComputeAreas())
