
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

    def get_lines(self):
        """
        Find the existing Guide Line Clusters group object
        """
        # Get left and right offsets from centerline
        left_offset = ofsets[0]
        right_offset = ofsets[1]

        # Computing coordinates and orthoginals for guidelines
        for sta in region_stations:
            if hasattr(alignment.Proxy, 'model'):
                coord, vec = alignment.Proxy.model.get_orthogonal( sta, "Left")
            else:
                coord, vec = self.line_orthogonal(alignment, sta, "Left")

            left_vec = copy.deepcopy(vec)
            right_vec = copy.deepcopy(vec)

            left_side = coord.add(left_vec.multiply(left_offset))
            right_side = coord.add(right_vec.negative().multiply(right_offset))

            left_line = Part.LineSegment(left_side, coord)
            right_line = Part.LineSegment(right_side, coord)

            # Generate guide line object and add to cluster
            shape = Part.Shape([left_line, right_line])
            wire = Part.Wire(shape.Edges)
            Part.show(wire)