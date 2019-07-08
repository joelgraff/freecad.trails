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

import DraftTools

from .... import resources

from ....alignment import alignment

from ...support import const, utils
from ...support.mouse_state import MouseState

from ...trackers.alignment_tracker import AlignmentTracker

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
        self.alignment = alignment.create(alignment_data, 'TEMP', True, False)
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

        #get all objects in the scene that are selectable.
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

        self.alignment_tracker = AlignmentTracker(
            self.doc, self.view, self.obj.Name, self.alignment
        )

        self.callbacks = {
            'SoKeyboardEvent': self.key_action,
            #    'SoMouseButtonEvent': self.button_action,
            #    'SoLocation2Event': self.mouse_action
        }

        self.doc.recompute()

        DraftTools.redraw3DView()

    def setup(self):
        """
        Initiailze the task window and controls
        """

        _mw = utils.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

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

        if self.view_objects:

            #reset line colors
            for _v in self.view_objects['line_colors']:
                _v[0].LineColor = _v[1]

            #reenable object selctables
            for _v in self.view_objects['selectable']:
                _v[0].Selectable = _v[1]

            self.view_objects.clear()

        #re-enable selection
        self.view.getSceneGraph().getField("selectionRole").setValue(1)

        #close dialog
        Gui.Control.closeDialog()

        #remove the callback for action
        if self.callbacks:

            for _k, _v in self.callbacks.items():
                self.view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        #delete the alignment object
        if self.alignment:
            self.doc.removeObject(self.alignment.Object.Name)
            self.alignment = None

        #shut down the tracker and re-select the object
        if self.pi_tracker:
            self.pi_tracker.finalize()
            self.pi_tracker = None
            Gui.Selection.addSelection(self.obj)

        if self.drag_tracker:
            self.drag_tracker.finalize()
            self.drag_tracker = None

        if self.alignment_tracker:
            self.alignment_tracker.finalize()
            self.alignment_tracker = None
