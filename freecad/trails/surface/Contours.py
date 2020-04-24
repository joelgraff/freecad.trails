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
from freecad.trails import ICONPATH
from ..project.support import utils
import os
import Draft


class CreateContour:
    """
    Command to create contour lines
    """

    def __init__(self):
        """
        Constructor
        """
        # Set icon,  menu text and tooltip
        self.resources = {
                'Pixmap': ICONPATH + '/icons/EditSurface.svg',
                'MenuText': "Create Contour",
                'ToolTip': "Create contour on selected surface."}

        # Get file path
        self.Path = os.path.dirname(__file__)

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return self.resources

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument is None:
            return False

        # Check for selected object
        if FreeCADGui.Selection.getSelection() is not None:
            selection = FreeCADGui.Selection.getSelection()[-1]
            if selection.TypeId == 'Mesh::Feature':
                return True
        return False

    def Activated(self):
        """
        Command activation method
        """
        # Get selected surface mesh
        surface = FreeCADGui.Selection.getSelection()[-1]
        base = surface.Mesh.Placement.Base
        copy_mesh = surface.Mesh.copy()
        copy_mesh.Placement.Base = FreeCAD.Vector(0, 0, base.z)

        # Create group for contour lines
        try:
            self.Contours = FreeCAD.ActiveDocument.Contours
        except Exception:
            FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Contours')
            self.Contours = FreeCAD.ActiveDocument.Contours

        self.CreateContour(copy_mesh, base)

    def CreateContour(self, Mesh, Base):
        """
        Create contour lines for selected surface
        """
        # Find max and min elevation of mesh
        zmax = Mesh.BoundBox.ZMax
        zmin = Mesh.BoundBox.ZMin

        # TODO DeltaH must be set by user
        DeltaH = 1000

        # Get point list and create contour lines
        for H in range(int(round(zmin)), int(round(zmax))):
            if H % int(DeltaH) == 0:
                CrossSections = Mesh.crossSections(
                    [((0, 0, H), (0, 0, 1))], 0.000001)

                for i in CrossSections[0]:
                    Contour = utils.make_wire(i, str(H/1000))
                    Contour.Label = str(H/1000)
                    Contour.Placement.move(FreeCAD.Vector(Base.x, Base.y, 0))
        FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand('Create Contour', CreateContour())
