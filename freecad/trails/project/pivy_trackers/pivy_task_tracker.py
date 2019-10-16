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
BaseTracker test class
"""

import FreeCAD as App
import FreeCADGui as Gui

from DraftTools import Modifier

from ... import resources

from ..tasks.alignment import base_tracker_test_task

from ..support.view_state import ViewState

class BaseTrackerTest(Modifier):
    """
    Command Description
    """
    def __init__(self, is_linked=False):
        """
        Constructor
        """

        self.doc = None
        self.task = None
        self.is_activated = False
        self.call = None
        self.tmp_group = None
        self.is_linked = is_linked

    def IsActive(self):
        """
        Activation condition requires one alignment be selected
        """

        if Gui.Control.activeDialog():
            return False

        if not App.ActiveDocument:
            return False

        selected = Gui.Selection.getSelection()

        if not selected:
            return False

        if not selected[0].Proxy.Type == 'Alignment':
            return False

        return True

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = resources.__path__[0] + '/icons/new_alignment.svg'

        _tool_tip = 'Tracker Test'

        if self.is_linked:
            _tool_tip += ' (linked)'
        else:
            _tool_tip += ' (unlinked)'

        return {'Pixmap'  : icon_path,
                'Accel'   : 'Ctrl+Shift+D',
                'MenuText': 'Draft Alignment',
                'ToolTip' : _tool_tip,
                'CmdType' : 'ForEdit'}

    def Activated(self):
        """
        Command activation method
        """

        self.doc = App.ActiveDocument

        #create working, non-visual copy of horizontal alignment
        obj = Gui.Selection.getSelection()[0]
        data = obj.Proxy.get_data_copy()

        self.doc = App.ActiveDocument
        ViewState().view = Gui.ActiveDocument.ActiveView

        #create alignment editing task
        self.task = \
            base_tracker_test_task.create(self.doc, data, obj, self.is_linked)

        Gui.Control.showDialog(self.task)
        self.task.setup()

        Modifier.Activated(self, 'BaseTrackerTest')

Gui.addCommand('BaseTrackerTest', BaseTrackerTest())
Gui.addCommand('BaseTrackerLinkedTest', BaseTrackerTest(True))
