# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************
"""
Manages template library UI
"""

import os

import FreeCAD as App
import FreeCADGui as Gui
from . import TemplateLibrary, SketchTemplate

class ViewTemplateLibrary():
    """
    View library class.
    Open the template library for selecting templates
    """
    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Ctrl+Alt+G",
                'MenuText': "Open Template Library",
                'ToolTip' : "Open the template library",
                'CmdType' : "ForEdit"}

    def _validate_tree(self):
        """
        Validate the tree of the active document, ensuring there is a
        templates folder
        """

        result = App.ActiveDocument.findObjects(
            'App::DocumentObjectGroup', 'Templates'
        )

        if not result:
            result = [
                App.ActiveDocument.addObject(
                    'App::DocumentObjectGroup', 'Templates'
                )
            ]

        return result[0]

    def _library_call_back(self, path):
        """
        Library Callback
        Merge the selected template into the project and add it to the
        templates group
        """

        #create a snapshot of the tree root where new objects will be merged
        snapshot = []

        for obj in App.ActiveDocument.RootObjects:
            snapshot += obj.Name

        #merge new objects
        App.ActiveDocument.mergeProject(path)

        #validate the template folder structure
        folder = self._validate_tree()

        #iterate the root objects, looking for objects not in the snapshot
        #relocate the skether objects
        new_objects = []

        for obj in App.ActiveDocument.RootObjects:

            if not obj.Name in snapshot:
                if obj.TypeId != 'Sketcher::SketchObject':
                    continue

                new_objects.append(obj.Name)
                _o = SketchTemplate.create(obj, obj.Label)
                folder.addObject(_o.Object)

        #remove the root objects...
        for obj_name in new_objects:
            App.ActiveDocument.removeObject(obj_name)

    def Activated(self):
        """
        Activation callback
        """
        TemplateLibrary.show(self._library_call_back)


Gui.addCommand('ViewTemplateLibrary', ViewTemplateLibrary())
