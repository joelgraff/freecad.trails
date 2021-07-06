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

    def area_between(self, tops, bottoms, i):
        """
        Calculate the areas above lower and below upper
        """
        bb_ymins = []
        bb_ymaxs = []
        bb_xmins = []
        bb_xmaxs = []
        for sec in tops + bottoms:
            sec_wire = sec.Shape.Wires[i]
            bb_ymins.append(sec_wire.BoundBox.YMin)
            bb_ymaxs.append(sec_wire.BoundBox.YMax)
            bb_xmins.append(sec_wire.BoundBox.XMin)
            bb_xmaxs.append(sec_wire.BoundBox.XMax)

        # Find the coords for the 'limits' box:
        area_minY = min(bb_ymins) - 1.0
        area_maxY = max(bb_ymaxs) + 1.0
        area_minX = min(bb_xmins) - 1.0
        area_maxX = max(bb_xmaxs) + 1.0

        ## Determine 4 edges for the 'limits' box:
        limit = [Part.makeLine((area_minX, area_minY, 0.0), (area_maxX, area_minY, 0.0)),
                Part.makeLine((area_maxX, area_minY, 0.0), (area_maxX, area_maxY, 0.0)),
                Part.makeLine((area_maxX, area_maxY, 0.0), (area_minX, area_maxY, 0.0)),
                Part.makeLine((area_minX, area_maxY, 0.0), (area_minX, area_minY, 0.0))]

        dellim = [Part.makeLine((area_minX, area_minY, 0.0), (area_minX+1, area_minY, 0.0)),
                Part.makeLine((area_minX+1, area_minY, 0.0), (area_minX+1, area_minY+1, 0.0)),
                Part.makeLine((area_minX+1, area_minY+1, 0.0), (area_minX, area_minY+1, 0.0)),
                Part.makeLine((area_minX, area_minY+1, 0.0), (area_minX, area_minY, 0.0))]

        face_area = Part.Face(Part.Wire(limit))
        del_area = Part.Face(Part.Wire(dellim))

        for top in tops:
            top_wire = top.Shape.Wires[i]
            fp_upper = top_wire.Vertexes[0].Point
            lp_upper = top_wire.Vertexes[-1].Point

            if fp_upper.x == lp_upper.x:
                return face_area.common(del_area)

            ## Add 3 edges to B to get a closed boundary:
            edges_top = top_wire.Edges + [Part.makeLine(fp_upper, (fp_upper[0], area_minY, 0.0)),
                                        Part.makeLine((fp_upper[0], area_minY, 0.0), (lp_upper[0], area_minY, 0.0)),
                                        Part.makeLine((lp_upper[0], area_minY, 0.0), lp_upper)]

            face_upper = Part.Face(Part.Wire(edges_top))
            face_area  = face_area.common(face_upper)

        for bottom in bottoms:
            bottom_wire = bottom.Shape.Wires[i]
            fp_lower = bottom_wire.Vertexes[0].Point
            lp_lower = bottom_wire.Vertexes[-1].Point

            if fp_lower.x == lp_lower.x:
                return face_area.common(del_area)

            ## Add 3 edges to A to get a closed boundary:
            edges_bottom = bottom_wire.Edges + [Part.makeLine(fp_lower, (fp_lower[0], area_maxY, 0.0)),
                                        Part.makeLine((fp_lower[0], area_maxY, 0.0), (lp_lower[0], area_maxY, 0.0)),
                                        Part.makeLine((lp_lower[0], area_maxY, 0.0), lp_lower)]

            face_lower = Part.Face(Part.Wire(edges_bottom))
            face_area  = face_area.common(face_lower)

        return face_area

    def get_areas(self, gl, tops, bottoms):
        shapes = []
        for i in range(len(gl.Shape.Wires)):
            result = self.area_between(tops, bottoms, i)
            shapes.append(result)

        return Part.makeCompound(shapes)
