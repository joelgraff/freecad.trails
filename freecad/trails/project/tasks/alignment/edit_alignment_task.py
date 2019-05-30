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
Task to edit an alignment
"""
from PySide import QtGui

import FreeCADGui as Gui

import Draft
import DraftTools

from .... import resources

from ....alignment import alignment_model

from ...support import const, utils
from ...support.mouse_state import MouseState

from ...trackers.pi_tracker import PiTracker
from ...trackers.drag_tracker import DragTracker
from ...trackers.alignment_tracker import AlignmentTracker

from .draft_alignment_task import DraftAlignmentTask

def create(doc, view, alignment_data, object_name):
    """
    Class factory method
    """
    return EditAlignmentTask(doc, view, alignment_data, object_name)

class EditAlignmentTask:
    """
    Task to manage alignment editing
    """

    class STYLES(const.Const):
        """
        Internal constants used to define ViewObject styles
        """

        DISABLED = [(0.4, 0.4, 0.4), 'Solid']
        ENABLED = [(0.8, 0.8, 0.8), 'Solid']
        HIGHLIGHT = [(0.0, 1.0, 0.0), 'Solid']
        PI = [(0.0, 0.0, 1.0), 'Solid']
        SELECTED = [(1.0, 0.8, 0.0), 'Solid']

    def __init__(self, doc, view, alignment_data, obj):

        self.panel = None
        self.view = view
        self.doc = doc
        self.obj = obj
        self.alignment = alignment_model.AlignmentModel()
        self.alignment.data = alignment_data
        self.pi_tracker = None
        self.drag_tracker = None
        self.alignment_tracker = None
        self.callbacks = {}
        self.mouse = MouseState()
        self.form = None
        self.ui_path = resources.__path__[0] + '/ui/'
        self.ui = self.ui_path + 'edit_alignment_task.ui'

        self.view_objects = {
            'selectables': [],
            'line_colors': [],
        }

        #disable selection entirely
        self.view.getSceneGraph().getField("selectionRole").setValue(0)

        #get all objects with LineColor and set them all to gray
        self.view_objects['line_colors'] = [
            (_v.ViewObject, _v.ViewObject.LineColor)
            for _v in self.doc.findObjects()
            if hasattr(_v, 'ViewObject')
            if hasattr(_v.ViewObject, 'LineColor')
        ]

        for _v in self.view_objects['line_colors']:
            self.set_vobj_style(_v[0], self.STYLES.DISABLED)

        #get all objects in the scene that are selecctable.
        self.view_objects['selectable'] = [
            (_v.ViewObject, _v.ViewObject.Selectable)
            for _v in self.doc.findObjects()
            if hasattr(_v, 'ViewObject')
            if hasattr(_v.ViewObject, 'Selectable')
        ]

        for _v in self.view_objects['selectable']:
            _v[0].Selectable = False

        #deselect existing selections
        Gui.Selection.clearSelection()

        _points = self.alignment.get_pi_coords()

        self.pi_tracker = PiTracker(
            self.doc, self.view, self.obj.Name, _points
        )

        self.alignment_tracker = AlignmentTracker(
            self.doc, self.view, self.obj.Name, self.alignment
        )

        self.callbacks = {
            'SoKeyboardEvent': self.key_action,
            'SoMouseButtonEvent': self.button_action,
            'SoLocation2Event': self.mouse_action
        }

        for _k, _v in self.callbacks.items():
            self.view.addEventCallback(_k, _v)

        self.doc.recompute()
        DraftTools.redraw3DView()

    def setup(self):
        """
        Initiailze the task window and controls
        """
        _mw = utils.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        #form.file_path = form.findChild(QtGui.QLineEdit, 'filename')
        #form.pick_file = form.findChild(QtGui.QToolButton, 'pick_file')
        #form.pick_file.clicked.connect(self.choose_file)
        #form.file_path.textChanged.connect(self.examine_file)

        self.form = form

    def accept(self):
        """
        Accept the task parameters
        """

        self.finish()

        return None

    def reject(self):
        """
        Reject the task
        """

        self.finish()

        return None

    def key_action(self, arg):
        """
        SoKeyboardEvent callback
        """

        if arg['Key'] == 'ESCAPE':
            self.finish()

    def button_action(self, arg):
        """
        SoLocation2Event callback for mouse / keyboard handling
        """

        pos = self.view.getCursorPos()
        self.mouse.update(arg, pos)

    def mouse_action(self, arg):
        """
        Mouse movement actions
        """

        _dragging = self.mouse.button1.dragging or self.mouse.button1.pressed

        #exclusive or - abort if both are true or false
        if not (self.drag_tracker is not None) ^ _dragging:
            return

        pos = self.view.getCursorPos()
        self.mouse.update(arg, pos)

        #if tracker exists, but we're not dragging, shut it down
        if self.drag_tracker:
            self.end_drag(arg, self.view.getPoint(pos))

        elif _dragging:

            self.start_drag(arg, self.view.getPoint(pos))

    def end_drag(self, arg, world_pos):
        """
        End drag operations with drag tracker
        """

        _coords = self.drag_tracker.get_transformed_coordinates('PI_TRACKER')

        self.pi_tracker.update(_coords)

        self.drag_tracker.finalize()
        self.pi_tracker.drag_mode = False
        self.drag_tracker = None

    def start_drag(self, arg, world_pos):
        """
        Begin drag operations with drag tracker
        """

        self.drag_tracker = DragTracker(
            self.view,
            [self.doc.Name, self.obj.Name, 'DRAG_TRACKER'],
            self.pi_tracker.node
        )

        #get selected geometry from the pi tracker
        _selected = [self.pi_tracker.get_selection_group()]

        #get selected geometry from the alignment tracker
        _selected.append(
            self.alignment_tracker.get_selection_group(
                self.pi_tracker.get_selected())
        )

        #get connection geometry from the pi tracker
        _connected = [self.pi_tracker.get_connection_group()]
        _connected.append(self.alignment_tracker\
            .get_connection_group(_selected[0].getChild(0))
        )

        self.drag_tracker.set_nodes(_selected, _connected, world_pos)

        self.drag_tracker.set_rotation_center(
            self.pi_tracker.get_selected()[0]
        )

        self.drag_tracker.callbacks.extend([
            self.pi_tracker.drag_callback,
            self.alignment_tracker.drag_callback
        ])

    def set_vobj_style(self, vobj, style):
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

    def finish(self):
        """
        Task cleanup
        """

        #reset line colors
        for _v in self.view_objects['line_colors']:
            _v[0].LineColor = _v[1]

        #reenable object selctables
        for _v in self.view_objects['selectable']:
            _v[0].Selectable = _v[1]

        #re-enable selection
        self.view.getSceneGraph().getField("selectionRole").setValue(1)

        #close dialog
        Gui.Control.closeDialog()

        #remove the callback for action
        if self.callbacks:

            for _k, _v in self.callbacks.items():
                self.view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        #shut down the tracker and re-select the object
        if self.pi_tracker:
            self.pi_tracker.finalize()
            self.pi_tracker = None
            Gui.Selection.addSelection(self.obj)

        if self.drag_tracker:
            self.drag_tracker.finalize()
            self.drag_tracker = None
