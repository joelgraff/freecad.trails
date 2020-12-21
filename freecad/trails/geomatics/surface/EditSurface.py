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
from pivy import coin
from freecad.trails import ICONPATH
import os


class AddTriangle:
    """
    Command to add a tirangle to mesh
    """

    def __init__(self):
        """
        Constructor
        """

        # Set icon,  menu text and tooltip
        self.resources = {
            'Pixmap': ICONPATH + '/icons/AddTriangle.svg',
            'MenuText': "Add Triangle",
            'ToolTip': "Add a triangle to selected surface."
                }

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
        return True

    def Activated(self):
        """
        Command activation method
        """
        # Call for Mesh.Addfacet function
        FreeCADGui.runCommand("Mesh_AddFacet")

FreeCADGui.addCommand('Add Triangle', AddTriangle())


class DeleteTriangle:
    """
    Command to delete a tirangle from mesh
    """

    def __init__(self):
        """
        Constructor
        """

        # Set icon,  menu text and tooltip
        self.resources = {
            'Pixmap': ICONPATH + '/icons/DeleteTriangle.svg',
            'MenuText': "Delete Triangle",
            'ToolTip': "Delete triangles from selected surface."
              }

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
        return True

    @staticmethod
    def Activated():
        """
        Command activation method
        """
        # Call for Mesh.RemoveComponents function
        FreeCADGui.runCommand("Mesh_RemoveComponents")


FreeCADGui.addCommand('Delete Triangle', DeleteTriangle())


class SwapEdge:
    """
    Command to swap an edge between two triangles
    """

    def __init__(self):
        """
        Constructor
        """

        # Set icon,  menu text and tooltip
        self.resources = {
            'Pixmap': ICONPATH + '/icons/SwapEdge.svg',
            'MenuText': "Swap Edge",
            'ToolTip': "Swap Edge of selected surface."
            }

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
        return True

    def Activated(self):
        """
        Command activation method
        """
        # Create an event callback for SwapEdge() function
        self.FaceIndexes = []
        self.MC = FreeCADGui.ActiveDocument.ActiveView.addEventCallbackPivy(
            coin.SoMouseButtonEvent.getClassTypeId(), self.SwapEdge)

    def SwapEdge(self, cb):
        """
        Take two triangle by mouse clicks and swap edge between them
        """
        # Get event
        event = cb.getEvent()

        # If mouse right button pressed finish swap edge operation
        if event.getButton() == coin.SoMouseButtonEvent.BUTTON2 \
                and event.getState() == coin.SoMouseButtonEvent.DOWN:
            FreeCADGui.ActiveDocument.ActiveView.removeEventCallbackPivy(
                coin.SoMouseButtonEvent.getClassTypeId(), self.MC)

        # If mouse left button pressed get picked point
        if event.getButton() == coin.SoMouseButtonEvent.BUTTON1 \
                and event.getState() == coin.SoMouseButtonEvent.DOWN:
            pickedPoint = cb.getPickedPoint()

            # Get triangle index at picket point
            if pickedPoint is not None:
                detail = pickedPoint.getDetail()

                if detail.isOfType(coin.SoFaceDetail.getClassTypeId()):
                    face_detail = coin.cast(
                        detail, str(detail.getTypeId().getName()))
                    index = face_detail.getFaceIndex()
                    self.FaceIndexes.append(index)

                    # try to swap edge between picked triangle
                    if len(self.FaceIndexes) == 2:
                        surface = FreeCADGui.Selection.getSelection()[-1]
                        CopyMesh = surface.Mesh.copy()

                        try:
                            CopyMesh.swapEdge(
                                self.FaceIndexes[0], self.FaceIndexes[1])

                        except Exception:
                            print("The edge between these triangles cannot be swappable")

                        surface.Mesh = CopyMesh
                        self.FaceIndexes.clear()

FreeCADGui.addCommand('Swap Edge', SwapEdge())


class SmoothSurface:
    """
    Command to smooth mesh surface
    """

    def __init__(self):
        """
        Constructor
        """

        # Set icon,  menu text and tooltip
        self.resources = {
            'Pixmap': ICONPATH + '/icons/SmoothSurface.svg',
            'MenuText': "Smooth Surface",
            'ToolTip': "Smooth selected surface."
            }

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
        return True

    @staticmethod
    def Activated():
        """
        Command activation method
        """
        # Get selected surface and smooth it
        surface = FreeCADGui.Selection.getSelection()[0]
        surface.Mesh.smooth()

FreeCADGui.addCommand('Smooth Surface', SmoothSurface())
