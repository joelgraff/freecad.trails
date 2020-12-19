# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2020 Hakan Seven <hakanseven12@gmail.com>             *
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
import Mesh
import numpy as np
import copy, math
import scipy.spatial

class SurfaceFunc:
    """
    This class is contain Surface Object functions.
    """
    def __init__(self):
        pass

    @staticmethod
    def triangulate(points):
        """
        Create 2D Delaunay triangulation.
        """
        # Normalize points
        base = points[0]
        nor_points = []
        for point in points:
            nor_points.append(point.sub(base))

        data = np.array(nor_points) 

        # Create delaunay triangulation
        tri = scipy.spatial.Delaunay(data[:, :2])
        delaunay = []

        for i in tri.vertices.tolist():
            delaunay.extend(i)

        return delaunay

    def test_delaunay(self, points, delaunay, lmax, amax):
        """
        Test delaunay for max length and max angle.
        """
        base = copy.deepcopy(points[0])
        base.z = 0
        index = []
        triangles = []
        mesh_index = []

        for i in range(0, len(delaunay), 3):
            first, second,third = delaunay[i:i+3]

            p1 = copy.deepcopy(points[first])
            p2 = copy.deepcopy(points[second])
            p3 = copy.deepcopy(points[third])
            p1.z = p2.z = p3.z = 0

            #Test triangle
            if self.max_length(lmax, p1, p2, p3)\
                and self.max_angle(amax,  p1, p2, p3):
                index.extend([first, second, third])
                triangles.extend([first, second, third, -1])

        for i in index:
            mesh_index.append(points[i].sub(base))

        return Mesh.Mesh(mesh_index), triangles


    @staticmethod
    def max_length(lmax, p1, p2, p3):
        """
        Calculation of the 2D length between triangle edges
        """
        # Calculate length between triangle vertices
        tri = [[p1, p2], [p2, p3], [p3, p1]]
        for i, j in tri:
            vec = i.sub(j)

            # Compare with input
            if vec.Length > lmax:
                return False
        return True

    @staticmethod
    def max_angle(amax, p1, p2, p3):
        """
        Calculation of the 2D angle between triangle edges
        """
        # Calculate angle between triangle vertices
        tri = [[p1, p2, p3], [p2, p3, p1], [p3, p1, p2]]
        for j, k, l in tri:
            vec1 = j.sub(k)
            vec2 = l.sub(k)
            radian = vec1.getAngle(vec2)
            degree = math.degrees(radian)

            # Compare with input
            if degree > amax:
                return False
        return True

    def contour_points(self, fpoint, mesh, deltaH):
        """
        Create contour lines for selected surface
        """

        # Find max and min elevation of mesh
        zmax = mesh.BoundBox.ZMax/1000
        zmin = mesh.BoundBox.ZMin/1000

        # Get point list and create contour points
        cont_points = []
        coords = []
        num_vert = []
        base = copy.deepcopy(fpoint)
        base.z = 0
        for H in range(int(round(zmin)), int(round(zmax))):
            if deltaH == 0: break
            if H % deltaH == 0:
                cont_points = mesh.crossSections(
                    [((0, 0, H*1000), (0, 0, 1))], 0.000001)

            if cont_points:
                for cont in cont_points[0]:
                    cont_up = []
                    for i in cont:
                        cont_up.append(i.add(base))
                    coords.extend(cont_up)
                    num_vert.append(len(cont_up))

        return coords, num_vert