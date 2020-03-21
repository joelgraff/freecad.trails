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

from .corridor.template import ViewTemplateLibrary
from . import resources
from .point import ImportPointFile, ExportPoints
from .surface import CreateSurface, EditSurface, Contours
from .section import CreateGuideLines
from . import GeoData

class CommandGroup:
    def __init__(self, cmdlist, menu, TypeId=None, tooltip=None):
        self.cmdlist = cmdlist
        self.menu = menu
        self.TypeId = TypeId
        if tooltip is None:
            self.tooltip = menu
        else:
            self.tooltip = tooltip

    def GetCommands(self):
        return tuple(self.cmdlist)

    def GetResources(self):
        return {'MenuText': self.menu, 'ToolTip': self.tooltip}

TRAILSWB_VERSION = '(alpha)'

class TrailsWorkbench(Gui.Workbench):
    """
    Class which gets initiated at startup of the GUI.
    """

    MenuText = 'Trails '+ TRAILSWB_VERSION
    ToolTip = 'Transportation Engineering Workbench'
    Icon = os.path.dirname(resources.__file__) + '/icons/workbench.svg'
    toolbox = []

    def __init__(self):

        #switch to True to enable development commands
        self.dev = False

        self.menu = 1
        self.toolbar = 2
        self.context = 4

        self.command_ui = {

            'Data Tools': {
                'gui': self.menu + self.toolbar,
                'cmd': ['Import Point File',
                        'Export Points',
                        'Geodata Tools'
                        ]
            },

            'Surface Tools': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': ['Create Surface',
                        'Surface Editor',
                        'Create Contour'
                        ]
            },

            'Section Tools': {
                'gui': self.menu + self.toolbar,
                'cmd': ['Create Guide Lines',
                        'Create Sections'
                        ]
            },

            'Alignment': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': ['ImportAlignmentCmd',
                        'EditAlignmentCmd',
                       ]
            },

            'Element Template': {
                'gui': self.menu + self.toolbar + self.context,
                'cmd': ['ViewTemplateLibrary',]
            },

            'Test': {
                'gui': self.menu + self.toolbar,
                'cmd': [
                    'BaseTrackerTest', 'BaseTrackerLinkedTest'
                ]
            },

            'Help': {
                'gui': self.toolbar,
                'cmd': ['TrailsGuide']
            }
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

    def Initialize(self):
        """
        Called when the workbench is first activated.
        """

        from .project.commands \
            import import_alignment_cmd, edit_alignment_cmd,\
                base_tracker_test, trails_guide_cmd

        for _k, _v in self.command_ui.items():

            if _v['gui'] & self.toolbar:
                self.appendToolbar(_k, _v['cmd'])

            if _v['gui'] & self.menu:
                self.appendMenu(_k, _v['cmd'])

    EditSurfaceSub = ['Add Triangle', 'Delete Triangle', 'Swap Edge', 
                      'Smooth Surface']
    Gui.addCommand('Surface Editor',
                   CommandGroup(EditSurfaceSub,
                                'Edit selected surface.',
                                TypeId='Mesh::Feature'))

    GeoData = ['Import OSM Map', 'Import CSV', 'Import GPX', 'Import Heights',
               'Import SRTM', 'Import XYZ', 'Import LatLonZ',  'Import Image', 
               'Import ASTER', 'Import LIDAR', 'Create House', 'Navigator',
               'ElevationGrid', 'Import EMIR',
               ]

    Gui.addCommand('Geodata Tools', 
                   CommandGroup(GeoData, 'Geodata Tools'))

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

print('ADDING TRAILS WORKBENCH....')
Gui.addWorkbench(TrailsWorkbench())
