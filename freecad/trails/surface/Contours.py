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
import os
import Draft


class CreateContour:

    def __init__(self):
        self.Path = os.path.dirname(__file__)

        self.resources = {
                'Pixmap': self.Path + '/../Resources/Icons/EditSurface.svg',
                'MenuText': "Create Contour",
                'ToolTip': "Create contour on selected surface."}

    def GetResources(self):

        # Return the command resources dictionary
        return self.resources

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False

        if FreeCADGui.Selection.getSelection() is not None:
            selection = FreeCADGui.Selection.getSelection()[-1]
            if selection.TypeId == 'Mesh::Feature':
                return True
        return False

    def Activated(self):
        surface = FreeCADGui.Selection.getSelection()[-1]
        base = surface.Mesh.Placement.Base
        copy_mesh = surface.Mesh.copy()

        # todo : try - except part should be changed
        try:
            self.Contours = FreeCAD.ActiveDocument.Contours
        except:
            self.Contours = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Contours')

        self.CreateContour(copy_mesh, base)

    def Wire(self, H, PointList, base, Support=None):
        Pl = FreeCAD.Placement()
        Pl.Rotation.Q = (0.0, 0.0, 0.0, 1.0)
        Pl.Base = FreeCAD.Vector(base.x, base.y, base.z)

        WireObj = FreeCAD.ActiveDocument.addObject(
            "Part::Part2DObjectPython", "_"+str(H))
        Draft._Wire(WireObj)
        WireObj.Points = PointList
        WireObj.Closed = False
        WireObj.Support = Support
        WireObj.MakeFace = False
        WireObj.Placement = Pl

        if FreeCADGui:
            Draft._ViewProviderWire(WireObj.ViewObject)
            Draft.formatObject(WireObj)
            Draft.select(WireObj)
            self.Contours.addObject(WireObj)
        FreeCAD.ActiveDocument.recompute()
        return WireObj

    def CreateContour(self, Mesh, Base):
        zmax = Mesh.BoundBox.ZMax
        zmin = Mesh.BoundBox.ZMin

        # TODO DeltaH must be set by user
        DeltaH = 1000

        for H in range(int(round(zmin)), int(round(zmax))):
            if H % int(DeltaH) == 0:
                CrossSections = Mesh.crossSections(
                    [((0, 0, H), (0, 0, 1))], 0.000001)

                for i in CrossSections[0]:
                    Contour = self.Wire(H, i, Base)
                    Contour.Label = str(H)

FreeCADGui.addCommand('Create Contour', CreateContour())
