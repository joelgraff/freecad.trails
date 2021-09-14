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
import Part
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
        slope = 1
        lenght = 30000
        self.origin = geo_origin.get()

        polyline = FreeCADGui.Selection.getSelection()[-2]
        self.target = FreeCADGui.Selection.getSelection()[-1]

        self.copy_shape = polyline.Shape.copy()
        self.copy_shape.Placement.move(self.origin.Origin)
        self.points = self.copy_shape.discretize(Distance=5000)

        self.pg = point_group.create()
        self.surf = surface.create()

        maxz = self.target.Mesh.BoundBox.ZMax
        minz = self.target.Mesh.BoundBox.ZMin
        fill_points = self.get_secpts(slope, minz)
        cut_points = self.get_secpts(slope, maxz)

        self.pg.Vectors = self.points + fill_points + cut_points
        self.surf.PointGroups = [self.pg]

    def get_secpts(self,slope, z):
        shape = self.copy_shape.copy()
        lenght = z - shape.Placement.Base.z
        shape.Placement.move(FreeCAD.Vector(0,0, slope*lenght))
        offpoints = shape.makeOffset2D(abs(lenght)).discretize(Angular=1,Curvature=100,Minimum=2)

        self.pg.Vectors = offpoints + self.points
        self.surf.PointGroups = [self.pg]

        intersec = self.surf.Mesh.intersect(self.target.Mesh)
        surf_pts = tuple((mp.Vector for mp in self.surf.Mesh.Points))
        target_pts = tuple((mp.Vector for mp in self.target.Mesh.Points))
        vects_intersec = tuple((mp.Vector for mp in intersec.Points))

        border = []
        for candidate in vects_intersec:
            if candidate not in surf_pts+target_pts:
                border.append(candidate.add(self.origin.Origin))

        wire_pts = [border.pop()]
        for i in range(len(border)):
            ref_pt = wire_pts[-1]
            dist = tuple((pt.distanceToPoint(ref_pt) for pt in border))
            idx = dist.index(min(dist))
            wire_pts.append(border.pop(idx))

        intsec = Part.makePolygon(wire_pts)
        intpts = intsec.discretize(Distance=5000)

        return intpts


FreeCADGui.addCommand('Create Pad', CreatePad())
