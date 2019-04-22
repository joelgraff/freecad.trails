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

import Draft
import DraftTools
from DraftTools import DraftTool, Creator

from ..support import utils, const
from ..support.utils import Constants as C
from ... import resources
from ...alignment import horizontal_alignment as hz_align
from ..tasks.alignment.draft_alignment_task import DraftAlignmentTask
from . import edit_tracker, wire_tracker

#from .edit_tracker import EditTracker

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

        self.button_states = {
            'Button1': False,
            'Button2': False,
            'Button3': False
        }
        self.pi_wire = None

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

        if self.doc is None:
            self.doc = App.ActiveDocument

        DraftTool.Activated(self, name=utils.translate('Alignment'))

        self.event_cb = self.view.addEventCallback("SoEvent", self.action)

        #get all objects with LineColor and set them all to gray
        self.view_objects['line_colors'] = \
            [
                (_v.ViewObject, _v.ViewObject.LineColor)
                for _v in App.ActiveDocument.findObjects()
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

        #create PI wire geometry
        self.pi_wire = utils.make_wire(
            pi_points, utils.get_uuid(), depth=C.Z_DEPTH[1]
        )

        self.set_style(self.pi_wire.ViewObject, self.STYLES.PI)

        self.tmp_group.addObject(self.pi_wire)
        self.tmp_group.addObject(self.alignment.Object)

        #get all objects with ViewObject.Selectable = True and
        #make them unselectable
        self.view_objects['selectables'] = \
            [_v.ViewObject for _v in App.ActiveDocument.findObjects()
             if hasattr(_v, 'ViewObject')
             if hasattr(_v.ViewObject, 'Selectable')
             if _v.ViewObject.Selectable
            ]

        for vobj in self.view_objects['selectables']:
            vobj.Selectable = False

        #create edit trackers for the PI geometry
        for point in pi_points:
            _et = edit_tracker.create(point, self.pi_wire.Name, 'PI')
            _et.set_style(self.STYLES.ENABLED)
            self.trackers[_et.name] = _et

        panel = DraftAlignmentTask(self.clean_up)

        Gui.Control.showDialog(panel)
        #panel.setup()

        self.is_activated = True

        App.ActiveDocument.recompute()

        self.wire_tracker = wire_tracker.WireTracker(self.pi_wire.Shape)

        DraftTools.redraw3DView()

    def action(self, arg):
        """
        Event handling for alignment drawing
        """

        print(arg)
        #trap the escape key to quit
        if arg['Type'] == 'SoKeyboardEvent':
            if arg['Key'] == 'ESCAPE':
                self.finish()
                return

        #trap mouse movement
        if arg['Type'] == 'SoLocation2Event':

            _p = Gui.ActiveDocument.ActiveView.getCursorPos()
            info = Gui.ActiveDocument.ActiveView.getObjectInfo(_p)

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

        #trap button clicks
        elif arg['Type'] == 'SoMouseButtonEvent':

            self.get_button_states(arg)

            _p = Gui.ActiveDocument.ActiveView.getCursorPos()
            info = Gui.ActiveDocument.ActiveView.getObjectInfo(_p)

            multi_select = arg['AltDown']

            _key, _it = self.get_current_tracker(info)

            #empty the arry and reset the trackers
            if self.selected_trackers:

                for _tracker in self.selected_trackers:
                    _tracker.set_style(self.STYLES.ENABLED)

                self.selected_trackers = []

            #current defined?  add it to the selection.
            if _it:

                while True:

                    _current = self.trackers[_key]
                    _current.set_style(self.STYLES.SELECTED)

                    self.selected_trackers.append(_current)

                    if not multi_select:
                        break

                    try:
                        _key = next(_it)
                    except StopIteration:
                        break

        App.ActiveDocument.recompute()
        DraftTools.redraw3DView()

    def set_button_states(self, arg):
        """
        Set the mouse button state dict
        """

        for _btn in self.button_states:
            self.button_states[_btn] = arg[_btn] == 'DOWN'

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

        #shut down trackers
        if self.trackers:

            for _v in self.trackers.values():
                _v.finalize()

            self.trackers.clear()

        self.selected_trackers = []
        self.active_tracker = None

        Creator.finish(self)

        self.is_activated = False

Gui.addCommand('EditAlignmentCmd', EditAlignmentCmd())
