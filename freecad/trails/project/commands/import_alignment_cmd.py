# -*- coding: utf-8 -*-
#***********************************************************************
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
Command to being alignment importing
"""
import os
import FreeCADGui as Gui

from ..tasks.alignment.import_alignment_task import ImportAlignmentTask


class ImportAlignmentCmd():
    """
    Initiates the ImportAlignmentTask class
    for 2D horizontal and vertical curves
    """
    def __init__(self):
        """
        Constructor
        """
        self.alignment_data = None

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "/../../resources/icons/import.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : 'Ctrl+Shift+A',
                'MenuText': 'Import Alignment',
                'ToolTip' :
                    'Import a horizontal or vertical alignment from LandXML',
                'CmdType' : 'ForEdit'}

    def Activated(self):
        """
        Command activation method
        """

        panel = ImportAlignmentTask()
        Gui.Control.showDialog(panel)
        panel.setup()

        return

Gui.addCommand('ImportAlignmentCmd', ImportAlignmentCmd())
