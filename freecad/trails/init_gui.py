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
from . import draft_init

from .design.corridor.template import ViewTemplateLibrary
from . import resources

TRAILSWB_VERSION = '(alpha)'

class CommandGroup:
    def __init__(self, cmdlist, menu, Type=None, tooltip=None):
        self.cmdlist = cmdlist
        self.menu = menu
        self.Type = Type
        if tooltip is None:
            self.tooltip = menu
        else:
            self.tooltip = tooltip

    def GetCommands(self):
        return tuple(self.cmdlist)

    def GetResources(self):
        return {'MenuText': self.menu, 'ToolTip': self.tooltip}

    def IsActive(self):
        """
        Define tool button activation situation
        """
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            # Check for selected object
            if FreeCADGui.Selection.getSelection():
                selection = FreeCADGui.Selection.getSelection()[-1]
                if selection.Proxy.Type == 'Trails::Surface':
                    return True
        """
        return True

class TrailsWorkbench(Gui.Workbench):
    """
    Class which gets initiated at startup of the GUI.
    """

    MenuText = 'Trails '+ TRAILSWB_VERSION
    ToolTip = 'Transportation and Geomatics Engineering Workbench'
    Icon = os.path.dirname(resources.__file__) + '/icons/workbench.svg'
    toolbox = []

    def __init__(self):

        #switch to True to enable development commands
        self.dev = False

        self.menu = 1
        self.toolbar = 2
        self.context = 4
        self.group = 8

        #dictionary key = name of command / command group.
        #'gui' - locations in gui where commands are accessed, (summed bitflags)
        #'cmd' - list of commands to display
        #'group' - Tuple containing the subgroup description and type.  None/undefined if no group
        self.command_ui = {

            'Data Tools': {
                'gui': self.menu + self.toolbar,
                'cmd': [
                    'Create Point Group',
                    'Import Point File',
                    'Export Points',
                    'Geo Import Tools'
                    ]
            },

            'Surface Tools': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': [
                    'Create Surface',
                    'Surface Editor'
                    ]
            },

            'Section Tools': {
                'gui': self.menu + self.toolbar,
                'cmd': [
                    'Create Region',
                    'Create Sections',
                    'Compute Areas',
                    'Create Table'
                    ]
            },

            'Alignment': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': [
                    'ImportAlignmentCmd',
                    'EditAlignmentCmd',
                    'CreateAlignmentFromLine'
                    ]
            },

            'Element Template': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': ['ViewTemplateLibrary']
            },

            'Help': {
                'gui': self.toolbar,
                'cmd': ['TrailsGuide']
            },

            'Surface Editor': {
                'gui': self.group,
                'cmd': [
                    'Add Point',
                    'Delete Triangle',
                    'Swap Edge',
                    'Smooth Surface'
                ],
                'tooltip': 'Edit selected surface',
                'type': 'Trails::Surface'
            },

            'Geo Import Tools': {
                'gui': self.group,
                'cmd': [
                    'Import OSM Map',
                    'Import CSV',
                    'Import GPX',
                    'Import Heights',
                    'Import SRTM',
                    'Import XYZ',
                    'Import LatLonZ',
                    'Import Image',
                    'Import ASTER',
                    'Import LIDAR',
                    'Create House',
                    'Navigator',
                    'ElevationGrid',
                    'Import EMIR',
               ],
               'tooltip': 'Geo Import Tools'
            },
        }

        if not self.dev:
            return

        #development commands
        self.command.ui = {
            **self.command.ui,
            **{
                'Test': {
                    'gui': self.menu,
                    'cmd': ['Command']
                }
            }
        }

    def GetClassName(self):
        """
        Return the workbench classname.
        """
        return 'Gui::PythonWorkbench'

    def import_module(self, path, name=None):
        """
        Return an import of a module specified by path and module name
        """

        _name_list = []

        if name:
            _name_list = [name]

        return __import__(path, globals(), locals(), _name_list)

    def Initialize(self):
        """
        Called when the workbench is first activated.
        """
        from .geomatics.point import import_points, export_points, create_pointgroup
        from .geomatics.surface import create_surface, edit_surface
        from .geomatics.region import create_region
        from .geomatics.section import create_sections
        from .geomatics.volume import compute_areas
        from .geomatics.table import create_table
        from .geomatics import geoimport_gui

        from .design.project.commands import create_alignment_from_line
        from .design.project.commands import import_alignment_cmd
        from .design.project.commands import edit_alignment_cmd
        from .design.project.commands import trails_guide_cmd

        for _k, _v in self.command_ui.items():

            if _v['gui'] & self.toolbar:
                self.appendToolbar(_k, _v['cmd'])

            if _v['gui'] & self.menu:
                self.appendMenu(_k, _v['cmd'])

            if _v['gui'] & self.group:
                Gui.addCommand(_k, CommandGroup(
                    _v['cmd'], _v['tooltip'], _v.get('type'))
                )

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
