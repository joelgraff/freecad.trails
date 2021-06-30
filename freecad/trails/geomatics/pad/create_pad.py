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
import Part, copy
from freecad.trails import ICONPATH, geo_origin
from ..surface import surface
from ..point import point_group


class CreatePad:
    """
    Command to create a new pad
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return {
            'Pixmap': ICONPATH + '/icons/CreateSurface.svg',
            'MenuText': "Create Pad",
            'ToolTip': "Create pad from selected closed polyline."
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
        origin = geo_origin.get()
        base = copy.deepcopy(origin.Origin)
        base.z = 0
        slope = 1
        lenght = 30000

        obj = FreeCADGui.Selection.getSelection()[-1]
        points = obj.Shape.discretize(Angular=1,Curvature=100,Minimum=2)

        shp = obj.Shape.copy()
        shp.Placement.move(FreeCAD.Vector(0,0, slope*lenght))
        offpoints = shp.makeOffset2D(lenght).discretize(Angular=1,Curvature=100,Minimum=2)

        result =[]
        for pt in offpoints+points:
            result.append(pt.add(base))

        pg = point_group.create()
        pg.Points = result
        surf = surface.create()
        surf.PointGroups = [pg]

FreeCADGui.addCommand('Create Pad', CreatePad())
