# -*- coding: utf-8 -*-
#**************************************************************************
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
Command to edit an alignment
"""

import FreeCAD as App
import FreeCADGui as Gui

from DraftTools import DraftTool

from ..support import utils

from ... import resources
from ...alignment import alignment as hz_align

from ..tasks.alignment import edit_alignment_task 

class EditAlignmentCmd(DraftTool):
    """
    Initiates and manages drawing activities for alignment creation
    """

    def __init__(self):
        """
        Constructor
        """

        self.doc = None
        self.view = None
        self.edit_alignment_task = None
        self.is_activated = False
        self.call = None
        self.tmp_group = None

        self.button_states = {
            'BUTTON1': False,
            'BUTTON2': False,
            'BUTTON3': False
        }

    def IsActive(self):
        """
        Activation condition requires one alignment be selected
        """

        if self.is_activated:
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

        return {'Pixmap'  : icon_path,
                'Accel'   : 'Ctrl+Shift+D',
                'MenuText': 'Draft Alignment',
                'ToolTip' : 'Draft a horizontal alignment',
                'CmdType' : 'ForEdit'}

    def Activated(self):
        """
        Command activation method
        """

        if self.is_activated:
            return

        self.doc = App.ActiveDocument

        #create working, non-visual copy of horizontal alignment
        obj = Gui.Selection.getSelection()[0]
        data = obj.Proxy.get_data_copy()

        DraftTool.Activated(self, name=utils.translate('Alignment'))

        self.doc = App.ActiveDocument
        self.view = Gui.ActiveDocument.ActiveView

        #self.call = self.view.addEventCallback('SoEvent', self.action)

        #create alignment editing task
        self.edit_alignment_task = \
            edit_alignment_task.create(self.doc, self.view, data, obj.Name)

        self.is_activated = True

    def action(self, arg):
        """
        Event handling for alignment drawing
        """

        #trap the escape key to quit
        if arg['Type'] == 'SoKeyboardEvent':
            if arg['Key'] == 'ESCAPE':

                self.finish()
                return

        #trap mouse movement
        if arg['Type'] == 'SoLocation2Event':
            pass

        #trap button clicks
        elif arg['Type'] == 'SoMouseButtonEvent':
            pass

    def handle_mouseover_tracker(self, info):
        """
        Handle mouseover activity when button is not pressed
        """

        _active = self.active_tracker

        _key, _it = self.get_current_tracker(info)

        _current = None

        if _it:
            _current = self.trackers[_key]

        #if we haven't moved off the previous tracker, we're done
        if _current == _active:
            return

        #_current is not None if a valid tracker was detected
        if _current:
            _current.set_style(self.STYLES.HIGHLIGHT)
            self.active_tracker = _current

        else:
            self.active_tracker = None

        if _active:
            _style = self.STYLES.ENABLED

            if _active in self.selected_trackers:
                _style = self.STYLES.SELECTED

            _active.set_style(_style)

    def get_button_states(self, arg):
        """
        Set the mouse button state dict
        """

        state = arg.get('State')
        button = arg.get('Button')

        print(state, button)
        if not state or not button:
            return

        self.button_states[button] = state == 'DOWN'

    def get_current_tracker(self, info):
        """
        Update tracker selection styles and states
        """

        if info:
            obj_name = info['Component']

            _it = iter(self.trackers)

            if 'Tracker' in obj_name:
                val = next(_x for _x in _it if _x == obj_name)
                return val, _it

        return None, None

    def clean_up(self):
        """
        Callback to finish the command
        """

        self.finish()

        return True

    def finish(self, closed=False, cont=False):
        """
        Finish drawing the alignment object
        """

        if self.edit_alignment_task:
            self.edit_alignment_task.finish()
            self.edit_alignment_task = None

        if self.call:
            self.view.removeEventCallback('SoEvent', self.action)

        self.is_activated = False

Gui.addCommand('EditAlignmentCmd', EditAlignmentCmd())
