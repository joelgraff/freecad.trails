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
import scipy.spatial

def max_length(lmax, P1, P2, P3):
    """
    Calculation of the 2D length between triangle edges
    """
    p1 = FreeCAD.Vector(P1[0], P1[1], 0)
    p2 = FreeCAD.Vector(P2[0], P2[1], 0)
    p3 = FreeCAD.Vector(P3[0], P3[1], 0)

    # Calculate length between triangle vertices
    List = [[p1, p2], [p2, p3], [p3, p1]]
    for i, j in List:
        D1 = i.sub(j)

        # Compare with input
        if D1.Length > lmax:
            return False
    return True

def max_angle(amax, P1, P2, P3):
    """
    Calculation of the 2D angle between triangle edges
    """
    import math
    p1 = FreeCAD.Vector(P1[0], P1[1], 0)
    p2 = FreeCAD.Vector(P2[0], P2[1], 0)
    p3 = FreeCAD.Vector(P3[0], P3[1], 0)

    # Calculate angle between triangle vertices
    List = [[p1, p2, p3], [p2, p3, p1], [p3, p1, p2]]
    for j, k, l in List:
        D1 = j.sub(k)
        D2 = l.sub(k)
        Radian = D1.getAngle(D2)
        Degree = math.degrees(Radian)

        # Compare with input
        if Degree > amax:
            return False
    return True

class SurfaceFunc:
    """
    This class is contain Surface Object functions.
    """

    def triangulate(points, lmax, amax):
        """
        Create 2D Delaunay triangulation.
        """
        # Normalize points
        base = points[0]
        nor_points = []
        for point in points:
            nor_points.append(point.sub(base))

        test = []
        for point in nor_points:
            x = point.x
            y = point.y
            z = point.z
            test.append((x, y, z))

        data = np.array(nor_points) 

        # Create delaunay triangulation
        tri = scipy.spatial.Delaunay(data[:, :2])
        index = []

        for i in tri.vertices:
            first = int(i[0])
            second = int(i[1])
            third = int(i[2])

            #Test triangle
            if max_length(lmax, data[first], data[second], data[third])\
                    and max_angle(amax, data[first], data[second], data[third]):
                index.extend([first, second, third, -1])

        return index

    def create_mesh(points, index):
        """
        Create a mesh for unwrited functions.
        """

        MeshList = []
        base = FreeCAD.Vector(points[0][0], points[0][1], 0.0)
        for i in index:
            if i == -1: continue
            MeshList.append(points[i].sub(base))

        mesh = Mesh.Mesh(MeshList)

        return mesh

    def contour_points(point, mesh, deltaH):
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
        base = FreeCAD.Vector(point[0], point[1], 0.0)
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