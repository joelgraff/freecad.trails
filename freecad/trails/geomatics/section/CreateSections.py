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

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui
from freecad.trails import ICONPATH
import MeshPart
import Draft
import os

class CreateSections:

    def __init__(self):

        self.Resources = {
            'Pixmap': ICONPATH + '/icons/CreateSections.svg',
            'MenuText': "Create Section Views",
            'ToolTip': "Create Section Views"
        }

        # Command to create sections for every selected surfaces.
        self.Path = os.path.dirname(__file__)

        # Import *.ui file(s)
        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreateSections.ui")

        # To Do List
        self.IPFui.CreateB.clicked.connect(self.CreateSections)
        self.IPFui.CancelB.clicked.connect(self.IPFui.close)

    def GetResources(self):
        # Return the command resources dictionary
        return self.Resources

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            return True
        return False

    def Activated(self):
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.IPFui.setParent(FreeCADGui.getMainWindow())
        self.IPFui.setWindowFlags(QtCore.Qt.Window)
        self.IPFui.show()

        self.IPFui.GLGCB.clear()

        try:
            self.GuideLines = FreeCAD.ActiveDocument.GuideLines
        except Exception:
            self.GuideLines = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'GuideLines')
            self.GuideLines.Label = "Guide Lines"

        GuideLinesGroup = self.GuideLines.Group
        self.GuideLinesList = []

        for group in GuideLinesGroup:
            if group.TypeId == 'App::DocumentObjectGroup':
                self.GuideLinesList.append(group.Name)
                self.IPFui.GLGCB.addItem(group.Label)

        self.IPFui.SelectSurfacesLW.clear()
        try:
            self.Surfaces = FreeCAD.ActiveDocument.Surfaces
        except Exception:
            self.Surfaces = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Surfaces')
            self.Surfaces.Label = "Surfaces"

        SurfacesGroup = self.Surfaces.Group
        self.SurfacesList = {}

        for surface in SurfacesGroup:
            self.SurfacesList[surface.Label] = surface
            self.IPFui.SelectSurfacesLW.addItem(surface.Label)

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


    def CreateSections(self):
        FreeCADVersion = FreeCAD.Version()
        if FreeCADVersion[0] == '0' and int(FreeCADVersion[1]) < 19:
            FreeCAD.Console.PrintError(
                "This feature is only available on versions > 0.18")
            return

        try:
            self.SectionsGroup = FreeCAD.ActiveDocument.Sections
        except Exception:
            self.SectionsGroup = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Sections')
            self.SectionsGroup.Label = "Sections"

        self.GuideLineIndex = self.IPFui.GLGCB.currentIndex()

        if self.GuideLineIndex < 0:
            FreeCAD.Console.PrintMessage(
                "No Guide Lines Group")
            return

        self.callback = self.view.addEventCallback("SoEvent",self.placeSecViews)

    def drawSecViews(self, pos):
        import math
        _position = pos
        _counter = 0
        _buffer = 50000

        GuideLineName = self.GuideLinesList[self.GuideLineIndex]
        guide_lines = FreeCAD.ActiveDocument.getObject(GuideLineName).Group

        multi_views_nor = math.ceil(len(guide_lines)**0.5)

        view_width =[]
        view_heigth =[]
        for guide_line in guide_lines:
            _origin = None
            for SelectedItem in self.IPFui.SelectSurfacesLW.selectedItems():
                _surface = self.SurfacesList[SelectedItem.text()]
                _points = []

                for _edge in guide_line.Shape.Edges:
                    _params = MeshPart.findSectionParameters(
                        _edge, _surface.Mesh, FreeCAD.Vector(0, 0, 1))
                    _params.insert(0, _edge.FirstParameter+1)
                    _params.append(_edge.LastParameter-1)

                    _values = [_edge.valueAt(i) for i in _params]
                    _points += _values

                section_points = MeshPart.projectPointsOnMesh(
                    _points, _surface.Mesh, FreeCAD.Vector(0, 0, 1))

                sec_points_2d = self.convert2View(section_points, _origin)
                _section = Draft.makeWire(sec_points_2d)

                view_width.append([min(i.x for i in sec_points_2d),
                    max(i.x for i in sec_points_2d)])
                view_heigth.append([min(i.y for i in sec_points_2d),
                    max(i.y for i in sec_points_2d)])

                _section.Placement.move(_position)
                self.SectionsGroup.addObject(_section)
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

        FreeCAD.ActiveDocument.recompute()
FreeCADGui.addCommand('Create Section Views', CreateSections())
