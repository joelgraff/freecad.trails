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
import Mesh, Part
import numpy as np
import copy, math
import scipy.spatial

import itertools as itools
from collections import Counter
from ast import literal_eval

class DataFunctions:
    """
    This class is contain Surface Data functions.
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
        index = []
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

        for i in index:
            mesh_index.append(points[i])

        return Mesh.Mesh(mesh_index)


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

    def get_contours(self, mesh, major, minor):
        """
        Create triangulation contour lines
        """
        # Find max and min elevation of mesh
        zmax = mesh.BoundBox.ZMax/1000
        zmin = mesh.BoundBox.ZMin/1000

        # Get point list and create contour points
        minor_contours = []
        major_contours = []

        delta = minor
        while delta < zmax:
            if minor == 0: break
            cross_sections = mesh.crossSections([((0, 0, delta*1000), (0, 0, 1))], 0.000001)

            for point_list in cross_sections[0]:
                if len(point_list) > 3:
                    wire = Part.makePolygon(point_list)

                    if delta % major == 0:
                        major_contours.append(wire)
                    else:
                        minor_contours.append(wire)

                    del point_list

            del cross_sections
            delta += minor

        majors = Part.makeCompound(major_contours)
        minors = Part.makeCompound(minor_contours)

        del major_contours, minor_contours

        return Part.makeCompound([majors, minors])

    def get_boundary(self, mesh):
        """
        Create triangulation boundary
        """
        facet_pidx = mesh.Topology[1]

        edges = itools.chain(*(itools.permutations(pidx, 2) for pidx in facet_pidx))
        count = Counter((str(edge) for edge in edges))

        double_boundary = list((literal_eval(k) for k, v in count.items() if v == 1))

        boundary = double_boundary[:1]
        for candidate in double_boundary[1:]:
            if candidate in boundary or candidate[::-1] in boundary:
                pass
            else:
                boundary.append(candidate)

        def mkEdge(p1, p2):
            return Part.makeLine((p1.x, p1.y, p1.z), (p2.x, p2.y, p2.z))

        points = mesh.Points
        edges = []
        for p1, p2 in boundary:
            edges.append(mkEdge(points[p1], points[p2]))

        wires = []
        for opening in Part.sortEdges(edges):
            wires.append(Part.Wire(opening))

        return Part.makeCompound(wires)


class ViewFunctions:
    """
    This class is contain Surface Data functions.
    """
    def __init__(self):
        pass

    def wire_view(self, shape, base, closed=False):
        points = []
        vertices = []
        copy_shape = shape.copy()
        copy_shape.Placement.move(base)

        for i in copy_shape.Wires:
            vectors = []
            for vertex in i.OrderedVertexes:
                vectors.append(vertex.Point)

            if closed:
                vectors.append(i.OrderedVertexes[0].Point)
            points.extend(vectors)
            vertices.append(len(vectors))

        del copy_shape

        return points, vertices

    def elevation_analysis(self, mesh, ranges):
        scale = (mesh.BoundBox.ZMax - mesh.BoundBox.ZMin) / 100
        colorlist = []

        for facet in mesh.Facets:
            z = facet.Points[0][2] + facet.Points[1][2] + facet.Points[2][2]
            zz = (z/3 - mesh.BoundBox.ZMin) / scale

            if zz < 20:
                colorlist.append((0.0, 1.0, 0.0))
            elif zz < 40:
                colorlist.append((0.0, 1.0, 1.0))
            elif zz < 60:
                colorlist.append((0.0, 0.0, 1.0))
            elif zz < 80:
                colorlist.append((1.0, 0.0, 1.0))
            else:
                colorlist.append((1.0, 0.0, 0.0))

        return colorlist

    def slope_analysis(self, mesh, ranges):
        colorlist = []
        for facet in mesh.Facets:
            normal = facet.Normal
            radian = normal.getAngle(FreeCAD.Vector(1, 1, 0))
            angle = math.degrees(radian)

            if angle < 45:
                colorlist.append((0.0, 1.0, 0.0))
            if angle < 90:
                colorlist.append((0.0, 1.0, 1.0))
            if angle < 135:
                colorlist.append((0.0, 0.0, 1.0))
            else:
                colorlist.append((1.0, 0.0, 1.0))

        return colorlist
