
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
Define Surface Object functions.
'''

import FreeCAD
import Part
import copy

class GLFunc:
    """
    This class is contain Surface Object functions.
    """
    def __init__(self):
        pass

    def line_orthogonal(self, line, distance, side=''):
        """
        Return the orthogonal vector pointing toward the indicated side at the
        provided position.  Defaults to left-hand side
        """

        _dir = 1.0

        _side = side.lower()

        if _side in ['r', 'rt', 'right']:
            _dir = -1.0

        start = line.Start
        end = line.End

        if (start is None) or (end is None):
            return None, None

        _delta = end.sub(start).normalize()
        _left = FreeCAD.Vector(-_delta.y, _delta.x, 0.0)

        _coord = start.add(_delta.multiply(distance*1000))

        return _coord, _left.multiply(_dir)

    def get_lines(self, fpoint, alignment, offsets, stations):
        """
        Find the existing Guide Line Clusters group object
        """
        wire_list = []

        # Get left and right offsets from centerline
        left_offset = offsets[0]
        right_offset = offsets[1]

        # Computing coordinates and orthoginals for guidelines
        for sta in stations:
            if hasattr(alignment.Proxy, 'model'):
                tuple_coord, tuple_vec = alignment.Proxy.model.get_orthogonal( sta, "Left")
                coord = FreeCAD.Vector(tuple_coord).sub(fpoint)
                vec = FreeCAD.Vector(tuple_vec)

            else:
                coord, vec = self.line_orthogonal(alignment, sta, "Left")

            left_vec = copy.deepcopy(vec)
            right_vec = copy.deepcopy(vec)

            left_side = coord.add(left_vec.multiply(left_offset))
            right_side = coord.add(right_vec.negative().multiply(right_offset))

            left_line = Part.LineSegment(left_side, coord)
            right_line = Part.LineSegment(right_side, coord)

            # Generate guide line object and add to cluster
            shape = Part.Shape([left_line,right_line])
            wire_list.append(Part.Wire(shape.Edges))

        return Part.makeCompound(wire_list)
