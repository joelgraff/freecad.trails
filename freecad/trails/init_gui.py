#/**********************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
GUI Initialization module
"""

import os
import FreeCADGui as Gui
from freecad.trails import ICONPATH


class TrailsWorkbench(Gui.Workbench):
    """
    Class which gets initiated at starup of the GUI.
    """

    MenuText = 'Trails Workbench'
    ToolTip = 'Transportation Engineering Workbench'
    Icon = os.path.join(ICONPATH, 'template_resource.svg')
    toolbox = []

    def __init__(self):

        self.menu = 1
        self.toolbar = 2
        self.context = 4

        self.command_ui = {

            'Transportation': {
                'gui': self.menu + self.toolbar,
                'cmd': ['NewProject']
            },

            'Alignment': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': ['ImportAlignmentCmd',
                        'GenerateVerticalAlignment',
                        'Generate3dAlignment'
                       ]
            },

            'Element Template': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': ['GenerateElementLoft', 'ViewTemplateLibrary']
            },

            'Element Loft': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': ['EditIntervals']
            },
        }

    def GetClassName(self):
        """
        Return the workbench classname.
        """
        return 'Gui::PythonWorkbench'

    def Initialize(self):
        """
        Called when the workbench is first activated.
        """

        for _k, _v in self.command_ui.items():

            if _v['gui'] & self.toolbar:
                self.appendToolbar(_k, _v['cmd'])

            if _v['gui'] & self.menu:
                self.appendMenu(_k, _v['cmd'])

        #self.init_dev_commands()

    def Activated(self):
        """
        Called when switching to this workbench
        """
        pass

    def Deactivated(self):
        """
        Called when switiching away from this workbench
        """
        pass

    def ContextMenu(self, recipient):
        """
        Right-click menu options
        """
        # "recipient" will be either "view" or "tree"

        for _k, _v in self.fn.items():
            if _v['gui'] & self.context:
                self.appendContextMenu(_k, _v['cmds'])

Gui.addWorkbench(TrailsWorkbench())
