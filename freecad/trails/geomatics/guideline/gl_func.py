
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

    def get_lines(self, fpoint, alignment, offsets, stations):
        """
        Find the existing Guide Line Clusters group object
        """
        gls = []

        # Get left and right offsets from centerline
        left_offset = offsets[0]
        right_offset = offsets[1]

        # Computing coordinates and orthoginals for guidelines
        for sta in stations:
            tuple_coord, tuple_vec = alignment.Proxy.model.get_orthogonal( sta, "Left")
            coord = FreeCAD.Vector(tuple_coord).sub(fpoint)
            vec = FreeCAD.Vector(tuple_vec)

            left_vec = copy.deepcopy(vec)
            right_vec = copy.deepcopy(vec)

            left_side = coord.add(left_vec.multiply(left_offset))
            right_side = coord.add(right_vec.negative().multiply(right_offset))

            # Generate guide line object and add to cluster
            gls.append(Part.makePolygon([left_side, coord, right_side]))

        return Part.makeCompound(gls)
