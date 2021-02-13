
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
import copy, math

class CSFunc:
    """
    This class is contain Surface Object functions.
    """
    def __init__(self):
        pass

    @staticmethod
    def convert2View(section, origin=None):
        import math
        sectionView = []

        if origin: section.insert(0, origin)
        sectionView.append(FreeCAD.Vector(0, 0, 0))

        for i in range(0, len(section)-1):
            virtual_point = FreeCAD.Vector(section[i+1].x, section[i+1].y, section[i].z)

            real_vector = section[i].sub(section[i+1])
            virtual_vector = section[i].sub(virtual_point)
            _length = real_vector.Length
            _angle = virtual_vector.getAngle(real_vector)

            dx = _length * math.cos(_angle)
            dy = _length * math.sin(_angle)

            if i == 0 and origin:
                side_point = FreeCAD.Vector(section[-1].x, section[-1].y, section[0].z)
                first_vector = section[0].sub(virtual_point)
                second_vector = virtual_point.sub(side_point)
                second_vector = first_vector.add(second_vector.normalize())
                if first_vector.Length > second_vector.Length: dx = -dx

            if virtual_vector.z < real_vector.z: dy = -dy
            sectionView.append(sectionView[-1].add(FreeCAD.Vector(dx, dy, 0)))

        sectionView.pop(0)
        return sectionView

    def placeSecViews(self, event):
        """
        Select section views location
        """
        try:
            if (event["Button"] == "BUTTON1") and (event["State"] == "DOWN"):
                clickPos = event["Position"]
                self.view.removeEventCallback("SoEvent", self.callback)
                position = self.view.getPoint(clickPos)
                self.drawSecViews(position)
        except Exception: pass


    def start_event(self):
        self.callback = self.view.addEventCallback("SoEvent",self.placeSecViews)

    def drawSecViews(self, pos):
        import math
        _position = pos
        _counter = 0
        _buffer = 50000

        selection = FreeCADGui.Selection.getSelection()

        if selection:
            if selection[-1].Proxy.Type == 'Trails::Guidelines':
                guide_lines = selection[-1]

                multi_views_nor = math.ceil(len(guide_lines.Shape.Wires)**0.5)

                view_width =[]
                view_heigth =[]
                wire_list = []
                for wire in guide_lines.Shape.Wires:
                    _origin = None
                    for SelectedItem in self.IPFui.SelectSurfacesLW.selectedItems():
                        _surface = self.SurfacesList[SelectedItem.text()]
                        _points = []

                        for _edge in wire.Edges:
                            _params = MeshPart.findSectionParameters(
                                _edge, _surface.Mesh, FreeCAD.Vector(0, 0, 1))
                            _params.insert(0, _edge.FirstParameter+1)
                            _params.append(_edge.LastParameter-1)

                            _values = [_edge.valueAt(i) for i in _params]
                            _points += _values

                        section_points = MeshPart.projectPointsOnMesh(
                            _points, _surface.Mesh, FreeCAD.Vector(0, 0, 1))

                        sec_points_2d = self.convert2View(section_points, _origin)

                        view_width.append([min(i.x for i in sec_points_2d),
                            max(i.x for i in sec_points_2d)])
                        view_heigth.append([min(i.y for i in sec_points_2d),
                            max(i.y for i in sec_points_2d)])

                        draw_sec = []
                        for i in sec_points_2d:
                            draw_sec.append(i.add(_position))

                        line_segments = []
                        for i in range(0, len(draw_sec)-1):
                            if draw_sec[i] == draw_sec[i+1]: continue
                            line_segments.append(Part.LineSegment(draw_sec[i], draw_sec[i+1]))

                        shape = Part.Shape(line_segments)
                        wire = Part.Wire(shape.Edges)
                        wire_list.append(wire)
                        _origin = section_points[0]

                    if _counter == multi_views_nor:
                        _dx = max(i[1] for i in view_width) - min(i[0] for i in view_width)
                        _shifting = _position.x - pos.x + _buffer
                        _reposition = FreeCAD.Vector(_dx + _shifting, 0, 0)
                        _position = pos.add(_reposition)
                        view_width.clear()
                        view_heigth.clear()
                        _counter = 0
                    else:
                        _dy = max(i[1] for i in view_heigth) - min(i[0] for i in view_heigth)
                        _reposition = FreeCAD.Vector(0, -(_dy + _buffer), 0)
                        _position = _position.add(_reposition)
                        view_heigth.clear()
                        _counter += 1

                _section = Part.makeCompound(wire_list)
                Part.show(_section)
