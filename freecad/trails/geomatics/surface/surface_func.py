# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
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

class SurfaceFunc:
    """
    This class is contain Surface Object functions.
    """

    def __init__(self):
        print("test")

    def create_mesh(points, index):
        """
        Create a mesh for unwrited functions.
        """

        MeshList = []
        for i in index:
            if i == -1: continue
            MeshList.append(points[i])

        mesh = Mesh.Mesh(MeshList)

        return mesh

    def contour_points(mesh, deltaH):
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
        for H in range(int(round(zmin)), int(round(zmax))):
            if deltaH == 0: break
            if H % deltaH == 0:
                cont_points = mesh.crossSections(
                    [((0, 0, H*1000), (0, 0, 1))], 0.000001)

            try:
                for cont in cont_points[0]:
                    coords.extend(cont)
                    num_vert.append(len(cont))

            except Exception: pass
        
        #FreeCAD.Console.PrintMessage(str(coords))

        return coords, num_vert

    def project_GL(self, GL, vector):
        pass
    