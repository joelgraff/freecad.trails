
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
import Part, MeshPart
import copy, math

class CSFunc:
    """
    This class is contain Surface Object functions.
    """
    def __init__(self):
        pass

    @staticmethod
    def section_converter(section_3d, origin=None):
        section_2d = []

        if origin: section_3d.insert(0, origin)
        section_2d.append(FreeCAD.Vector(0, 0, 0))

        for i in range(0, len(section_3d)-1):
            virtual_point = copy.deepcopy(section_3d[i+1])
            virtual_point.z = section_3d[i].z

            real_vector = section_3d[i].sub(section_3d[i+1])
            virtual_vector = section_3d[i].sub(virtual_point)
            length = real_vector.Length
            angle = virtual_vector.getAngle(real_vector)

            dx = length * math.cos(angle)
            dy = length * math.sin(angle)

            if i == 0 and origin:
                side_point = copy.deepcopy(section_3d[-1])
                side_point.z = section_3d[0].z

                first_vector = section_3d[0].sub(virtual_point)
                second_vector = virtual_point.sub(side_point)
                second_vector = first_vector.add(second_vector.normalize())
                if first_vector.Length > second_vector.Length: dx = -dx

            if virtual_vector.z < real_vector.z: dy = -dy
            section_2d.append(section_2d[-1].add(FreeCAD.Vector(dx, dy, 0)))

        section_2d.pop(0)
        return section_2d

    def create_3d_sections(self, gl, surface)
        wire_list = []
        for wire in gl.Shape.Wires:

            points = []
            for edge in wire.Edges:
                params = MeshPart.findSectionParameters(
                    edge, surface.Mesh, FreeCAD.Vector(0, 0, 1))
                params.insert(0, edge.FirstParameter+1)
                params.append(edge.LastParameter-1)

                values = [edge.valueAt(i) for i in params]
                points += values

            section_3d = MeshPart.projectPointsOnMesh(
                points, surface.Mesh, FreeCAD.Vector(0, 0, 1))

            line_segments = []
            for i in range(0, len(section_3d)-1):
                if section_3d[i] == section_3d[i+1]: continue
                line_segments.append(Part.LineSegment(section_3d[i], section_3d[i+1]))

            shape = Part.Shape(line_segments)
            wire = Part.Wire(shape.Edges)
            wire_list.append(wire)

        sections3d = Part.makeCompound(wire_list)
        return sections3d

    def draw_2d_sections(self, position, gl, group):
        counter = 0
        buffer = 50000
        pos = position

        multi_views_nor = math.ceil(len(guidelines.Shape.Wires)**0.5)

        view_width =[]
        view_heigth =[]
        wire_list = []
        for i, wire in enumerate(guidelines.Shape.Wires):

            origin = None
            for section in group:

                section_3d = []
                for vertex in section.Shape.Wires[i].Vertexes:
                    section_3d.append(vertex.Point)

                section_2d = self.section_converter(section_3d, origin)

                view_width.append([min(i.x for i in section_2d),
                    max(i.x for i in section_2d)])
                view_heigth.append([min(i.y for i in section_2d),
                    max(i.y for i in section_2d)])

                draw_sec = []
                for i in section_2d:
                    draw_sec.append(i.add(position))

                line_segments = []
                for i in range(0, len(draw_sec)-1):
                    if draw_sec[i] == draw_sec[i+1]: continue
                    line_segments.append(Part.LineSegment(draw_sec[i], draw_sec[i+1]))

                shape = Part.Shape(line_segments)
                wire = Part.Wire(shape.Edges)
                wire_list.append(wire)
                origin = section_3d[0]

            if counter == multi_views_nor:
                dx = max(i[1] for i in view_width) - min(i[0] for i in view_width)
                shifting = position.x - pos.x + buffer
                reposition = FreeCAD.Vector(dx + shifting, 0, 0)
                position = pos.add(reposition)
                view_width.clear()
                view_heigth.clear()
                counter = 0
            else:
                dy = max(i[1] for i in view_heigth) - min(i[0] for i in view_heigth)
                reposition = FreeCAD.Vector(0, -(dy + buffer), 0)
                position = position.add(reposition)
                view_heigth.clear()
                counter += 1

        section_draws = Part.makeCompound(wire_list)
        return section_draws
