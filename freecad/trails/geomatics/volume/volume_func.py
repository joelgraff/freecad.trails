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

'''
Define Volume Object functions.
'''
import FreeCAD
import Part



class VolumeFunc:
    """
    This class is contain Volume Object functions.
    """
    def __init__(self):
        pass

    def area_between(self, lower, upper):
        """
        Calculate the areas above lower and below upper
        """
        bb_lower = lower.BoundBox
        bb_upper = upper.BoundBox

        # Find the coords for the 'limits' box:
        area_minX = max(bb_lower.XMin, bb_upper.XMin) - 1.0
        area_maxX = min(bb_lower.XMax, bb_upper.XMax) + 1.0
        area_minY = min(bb_lower.YMin, bb_upper.YMin) - 1.0
        area_maxY = max(bb_lower.YMax, bb_upper.YMax) + 1.0

        fp_lower = lower.Vertexes[0].Point
        lp_lower = lower.Vertexes[-1].Point

        fp_upper = upper.Vertexes[0].Point
        lp_upper = upper.Vertexes[-1].Point

        ## Add 3 edges to A to get a closed boundary:
        edgesA = lower.Edges + [Part.makeLine(fp_lower, (fp_lower[0], area_maxY, 0.0)),
                                Part.makeLine((fp_lower[0], area_maxY, 0.0), (lp_lower[0], area_maxY, 0.0)),
                                Part.makeLine((lp_lower[0], area_maxY, 0.0), lp_lower)]

        ## Add 3 edges to B to get a closed boundary:
        edgesB = upper.Edges + [Part.makeLine(fp_upper, (fp_upper[0], area_minY, 0.0)),
                                Part.makeLine((fp_upper[0], area_minY, 0.0), (lp_upper[0], area_minY, 0.0)),
                                Part.makeLine((lp_upper[0], area_minY, 0.0), lp_upper)]

        ## Determine 4 edges for the 'limits' box:
        edgesLim = [Part.makeLine((area_minX, area_minY, 0.0), (area_maxX, area_minY, 0.0)),
                    Part.makeLine((area_maxX, area_minY, 0.0), (area_maxX, area_maxY, 0.0)),
                    Part.makeLine((area_maxX, area_maxY, 0.0), (area_minX, area_maxY, 0.0)),
                    Part.makeLine((area_minX, area_maxY, 0.0), (area_minX, area_minY, 0.0))]

        face_lower = Part.Face(Part.Wire(edgesA))
        face_upper = Part.Face(Part.Wire(edgesB))
        face_limit = Part.Face(Part.Wire(edgesLim))

        area_lower = face_lower.common(face_limit)
        area_upper = face_upper.common(face_limit)
        face_area  = area_lower.common(area_upper)

        return face_area

    def test(self, selection):
        shapes = []

        project = selection[0]
        ground = selection[1]

        for i in range(len(project.Shape.Wires)):
            prj = project.Shape.Wires[i]
            grd = ground.Shape.Wires[i]
            result = self.area_between(prj, grd)
            shapes.append(result)

        Part.show(Part.makeCompound(shapes))
