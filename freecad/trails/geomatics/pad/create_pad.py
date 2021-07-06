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
            'Pixmap': ICONPATH + '/icons/CreatePad.svg',
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

        polyline = FreeCADGui.Selection.getSelection()[-2]
        target = FreeCADGui.Selection.getSelection()[-1]
        points = polyline.Shape.discretize(Distance=5000)

        shp = polyline.Shape.copy()
        shp.Placement.move(FreeCAD.Vector(0,0, slope*lenght))
        offpoints = shp.makeOffset2D(lenght).discretize(Angular=1,Curvature=100,Minimum=2)

        result =[]
        for pt in offpoints+points:
            result.append(pt.add(base))

        pg = point_group.create()
        pg.Points = result
        surf = surface.create()
        surf.MaxLength = 100000
        surf.PointGroups = [pg]

        intersec = surf.Mesh.intersect(target.Mesh)
        surf_pts = tuple((mp.Vector for mp in surf.Mesh.Points))
        target_pts = tuple((mp.Vector for mp in target.Mesh.Points))
        vects_intersec = tuple((mp.Vector for mp in intersec.Points))

        border = []
        for candidate in vects_intersec:
            if candidate not in surf_pts+target_pts:
                border.append(candidate)

        wire_pts = [border.pop()]
        for i in range(len(border)):
            ref_pt = wire_pts[-1]
            dist = tuple((pt.distanceToPoint(ref_pt) for pt in border))
            idx = dist.index(min(dist))
            wire_pts.append(border.pop(idx))

        intsec = Part.makePolygon(wire_pts)
        intpts = intsec.discretize(Distance=5000)

        result =[]
        for pt in intpts+points:
            result.append(pt.add(base))

        pg.Points = result
        surf.PointGroups = [pg]

FreeCADGui.addCommand('Create Pad', CreatePad())
