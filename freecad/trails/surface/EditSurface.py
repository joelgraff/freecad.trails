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
import os


class AddTriangle:

    def __init__(self):

        self.Path = os.path.dirname(__file__)

        self.resources = {
            'Pixmap': self.Path + '/../Resources/Icons/EditSurface.svg',
            'MenuText': "Add Triangle",
            'ToolTip': "Add a triangle to selected surface."
                }

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
        FreeCADGui.runCommand("Mesh_AddFacet")

FreeCADGui.addCommand('Add Triangle', AddTriangle())


class DeleteTriangle:

    def __init__(self):
        self.Path = os.path.dirname(__file__)

        self.resources = {
            'Pixmap': self.Path + '/../Resources/Icons/EditSurface.svg',
            'MenuText': "Delete Triangle",
            'ToolTip': "Delete triangles from selected surface."
              }

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

    @staticmethod
    def Activated():
        FreeCADGui.runCommand("Mesh_RemoveComponents")


FreeCADGui.addCommand('Delete Triangle', DeleteTriangle())


class SwapEdge:

    def __init__(self):
        self.Path = os.path.dirname(__file__)

        self.resources = {
            'Pixmap': self.Path + '/../Resources/Icons/EditSurface.svg',
            'MenuText': "Swap Edge",
            'ToolTip': "Swap Edge of selected surface."
            }

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
        self.FaceIndexes = []
        self.MC = FreeCADGui.ActiveDocument.ActiveView.addEventCallbackPivy(
            coin.SoMouseButtonEvent.getClassTypeId(), self.SwapEdge)

    def SwapEdge(self, cb):
        event = cb.getEvent()
        if event.getButton() == coin.SoMouseButtonEvent.BUTTON2 \
                and event.getState() == coin.SoMouseButtonEvent.DOWN:
            FreeCADGui.ActiveDocument.ActiveView.removeEventCallbackPivy(
                coin.SoMouseButtonEvent.getClassTypeId(), self.MC)
        if event.getButton() == coin.SoMouseButtonEvent.BUTTON1 \
                and event.getState() == coin.SoMouseButtonEvent.DOWN:
            pp = cb.getPickedPoint()

            if pp is not None:
                detail = pp.getDetail()

                if detail.isOfType(coin.SoFaceDetail.getClassTypeId()):
                    face_detail = coin.cast(
                        detail, str(detail.getTypeId().getName()))
                    index = face_detail.getFaceIndex()
                    self.FaceIndexes.append(index)

                    if len(self.FaceIndexes) == 2:
                        surface = FreeCADGui.Selection.getSelection()[-1]
                        CopyMesh = surface.Mesh.copy()

                        try:
                            CopyMesh.swapEdge(
                                self.FaceIndexes[0], self.FaceIndexes[1])

                        except Exception:
                            pass

                        surface.Mesh = CopyMesh
                        self.FaceIndexes.clear()

FreeCADGui.addCommand('Swap Edge', SwapEdge())


class SmoothSurface:

    def __init__(self):
        self.Path = os.path.dirname(__file__)

        self.resources = {
            'Pixmap': self.Path + '/../Resources/Icons/EditSurface.svg',
            'MenuText': "Smooth Surface",
            'ToolTip': "Smooth selected surface."
            }

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

    @staticmethod
    def Activated():
        surface = FreeCADGui.Selection.getSelection()[0]
        surface.Mesh.smooth()

FreeCADGui.addCommand('Smooth Surface', SmoothSurface())
