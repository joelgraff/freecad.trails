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
from . import gl_cluster
from freecad.trails.design.alignment import alignment_group


class CreateGuidelines:
    """
    Command to create a new Guidelines
    """

    def __init__(self):
        """
        Command to create guide lines for selected alignment.
        """
        pass

    def GetResources(self):
        # Return the command resources dictionary
        return {
            'Pixmap': ICONPATH + '/icons/CreateGuideLines.svg',
            'MenuText': "Create Guidelines",
            'ToolTip': "Create guidelines for selected alignment"
            }

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            return True
        return False

    def Activated(self):

        # Check for selected object
        alignments = alignment_group.get()
        selection = FreeCADGui.Selection.getSelection()

        # Check that the Alignments Group has objects
        if len(alignments.Group) == 0:
            FreeCAD.Console.PrintMessage(
                "Please add an Alignment or Wire to the Alignment Group")
            return

        try:
            gl_cluster.create(selection[-1])
        except Exception:
            FreeCAD.Console.PrintMessage(
                "Please select an Alignment or Wire")

FreeCADGui.addCommand('Create Guidelines', CreateGuidelines())
