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
from pivy import coin
import Draft
import DraftTools
from DraftTools import DraftTool, Creator
from DraftTrackers import Tracker
from ..support import utils, const
from ..support.utils import Constants as C
from ... import resources
from ...alignment import horizontal_alignment as hz_align
from ..tasks.alignment.draft_alignment_task import DraftAlignmentTask
from . import wire_tracker

class EditAlignmentCmd(DraftTool):
    """
    Initiates and manages drawing activities for alignment creation
    """

    class STYLES(const.Const):
        """
        Internal constants used to define ViewObject styles
        """

        DISABLED =  [(0.4, 0.4, 0.4), 'Solid']
        ENABLED =   [(0.8, 0.8, 0.8), 'Solid']
        HIGHLIGHT = [(0.0, 1.0, 0.0), 'Solid']
        PI =        [(0.0, 0.0, 1.0), 'Solid']
        SELECTED =  [(1.0, 0.8, 0.0), 'Solid']

    def __init__(self):
        """
        Constructor
        """

        self.doc = None

        self.view_objects = {
            'selectables': [],
            'line_colors': []
        }

        self.tmp_group = None
        self.alignment = None
        self.is_activated = False
        self.event_cb = None
        self.trackers = {}
        self.active_tracker = None
        self.selected_trackers = []
        self.drag_tracker = None
        self.radius_tracker = None

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

        if not selected[0].Proxy.Type == 'HorizontalAlignment':
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

        DraftTool.Activated(self, name=utils.translate('Alignment'))

        self.doc = App.ActiveDocument
        self.view = Gui.ActiveDocument.ActiveView

        #set up callback for SoEvents
        self.event_cb = self.view.addEventCallback("SoEvent", self.action)

        #disable selection entirely
        self.view.getSceneGraph().getField("selectionRole").setValue(0)

        #get all objects with LineColor and set them all to gray
        self.view_objects['line_colors'] = \
            [
                (_v.ViewObject, _v.ViewObject.LineColor)
                for _v in self.doc.findObjects()
                if hasattr(_v, 'ViewObject')
                if hasattr(_v.ViewObject, 'LineColor')
            ]

        for _v in self.view_objects['line_colors']:
            self.set_style(_v[0], self.STYLES.DISABLED)

        #create temporary group
        self.tmp_group = self.doc.addObject('App::DocumentObjectGroup', 'Temp')

        #create working, non-visual copy of horizontal alignment
        data = Gui.Selection.getSelection()[0].Proxy.get_data_copy()
        self.alignment = hz_align.create(data, utils.get_uuid(), True)

        #deselect existing selections
        Gui.Selection.clearSelection()

        pi_points = self.alignment.get_pi_coords()

        #create PI wire tracker geometry
        self.wire_tracker = wire_tracker.create(
            self.doc, 'Sugar_Grove_Rd_Horiz', pi_points
        )

        self.tmp_group.addObject(self.alignment.Object)

        panel = DraftAlignmentTask(self.clean_up)

        Gui.Control.showDialog(panel)
        #panel.setup()

        self.is_activated = True

        self.doc.recompute()
        DraftTools.redraw3DView()

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
            
            _p = self.view.getCursorPos()
            _pt = self.view.getPoint(_p)
            info = self.view.getObjectInfo(_p)

            if info:
                print(info)

            return

            if not self.button_states['BUTTON1']:
                self.handle_mouseover_tracker(info)
            else:
                self.handle_drag_tracker(
                    self.view.getPoint(_p)
                )

        #trap button clicks
        elif arg['Type'] == 'SoMouseButtonEvent':

            self.get_button_states(arg)

            _p = self.view.getCursorPos()
            info = self.view.getObjectInfo(_p)

            multi_select = arg['AltDown']

            _key, _it = self.get_current_tracker(info)

            #empty the arry and reset the trackers
            if self.selected_trackers:

                for _tracker in self.selected_trackers:
                    _tracker.set_style(self.STYLES.ENABLED)

                self.selected_trackers = []

            #current defined?  add it to the selection.
            if _it:

                #Clear the button states so dragging won't work unles
                for _v in self.button_states.values():
                    _v = False

                while True:

                    _current = self.trackers[_key]
                    _current.set_style(self.STYLES.SELECTED)

                    self.active_tracker = _current
                    self.selected_trackers.append(_current)

                    if not multi_select:
                        break

                    try:
                        _key = next(_it)

                    except StopIteration:
                        break

                

        self.doc.recompute()
        DraftTools.redraw3DView()

    def handle_drag_tracker(self, point):
        """
        Handle dragging activity when button is pressed
        """

        if not self.active_tracker:
            return

        #if self.drag_tracker is None:
           # self.drag_tracker = drag_tracker.create(self.pi_wire.Points)

        pl = App.Placement()
        pl.Base = point.sub(self.active_tracker.position)

        self.drag_tracker.set_placement(pl)


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

    def set_style(self, vobj, style):
        """
        Set the view object style based on the passed style tuple
        """

        vobj.LineColor = style[0]
        vobj.DrawStyle = style[1]

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

        #finalize tracking
        #if self.ui:
            #if hasattr(self, 'alignment_tracker'):
                #self.alignment_tracker.finalize()

        #delete the temproary geometry
        self.tmp_group.removeObjectsFromDocument()
        self.doc.removeObject(self.tmp_group.Name)

        #reset selctable object values
        for _v in self.view_objects['selectables']:
            _v.Selectable = True

        #reset line colors
        for _v in self.view_objects['line_colors']:
            _v[0].LineColor = _v[1]

        #close dialog
        if not Draft.getParam('UiMode', 1):
            Gui.Control.closeDialog()

        #remove the callback for action
        if self.call:
            self.view.removeEventCallback("SoEvent", self.call)

        #shut down tracker
        if self.wire_tracker:
            self.wire_tracker.finalize()

        #re-enable selection
        self.view.getSceneGraph().getField("selectionRole").setValue(1)

        Creator.finish(self)

        self.is_activated = False

Gui.addCommand('EditAlignmentCmd', EditAlignmentCmd())
