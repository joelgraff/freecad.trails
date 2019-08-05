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
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

from pivy import coin

import FreeCAD as App
from FreeCAD import Vector
import FreeCADGui as Gui

import DraftTools

from .... import resources

from ...support import utils

from ...support.drag_state import DragState
from ...support.mouse_state import MouseState
from ...support.view_state import ViewState

from ...trackers.box_tracker import BoxTracker
from ...trackers.base_tracker import BaseTracker
from ...trackers.wire_tracker import WireTracker
from ...trackers.grid_tracker import GridTracker

from ...trackers.coin_style import CoinStyle

class SpriteSplitterTask:
    """
    Task to manage alignment editing
    """

    def __init__(self, doc):


        self.ui_path = resources.__path__[0] + '/ui/'
        self.ui = self.ui_path + 'sprite_splitter_task_panel.ui'

        self.form = None
        self.subtask = None

        self.panel = None
        self.doc = doc

        self.plane = None
        self.names = ['FreeCAD', self.doc.Name, 'Sprite Splitter']

        self.image = QtGui.QImage()

        self.cursor_trackers = [
            WireTracker(self.names), WireTracker(self.names[:2] + ['CURSOR'])
        ]

        self.rubberband_tracker = BoxTracker(self.names[:2] + ['RUBBERBAND'])
        self.rubberband_tracker.set_selectability(False)

        self.node = BaseTracker(self.names)

        self.node.insert_node(self.cursor_trackers[0].switch)
        self.node.insert_node(self.cursor_trackers[1].switch)
        self.node.insert_node(self.rubberband_tracker.switch)

        #deselect existing selections
        Gui.Selection.clearSelection()

        self.callbacks = {
            'SoLocation2Event':
            ViewState().view.addEventCallback(
                'SoLocation2Event', self.mouse_event),

            'SoMouseButtonEvent':
            ViewState().view.addEventCallback(
                'SoMouseButtonEvent', self.button_event)
        }

        self.grid_tracker = GridTracker(self.names)

        DraftTools.redraw3DView()

    def setup(self):
        """
        Initiailze the task window and controls
        """
        _mw = utils.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        form.file_path = form.findChild(QtGui.QLineEdit, 'filename')
        form.pick_file = form.findChild(QtGui.QToolButton, 'pick_file')
        form.pick_file.clicked.connect(self.choose_file)

        form.grid_params = [
            form.findChild(QtGui.QSpinBox, 'grid_dim_h_val'),
            form.findChild(QtGui.QSpinBox, 'grid_dim_v_val'),
            form.findChild(QtGui.QSpinBox, 'grid_size_h_val'),
            form.findChild(QtGui.QSpinBox, 'grid_size_v_val'),
            form.findChild(QtGui.QSpinBox, 'grid_pad_h_val'),
            form.findChild(QtGui.QSpinBox, 'grid_pad_v_val'),
            form.findChild(QtGui.QSpinBox, 'border_pad_h_val'),
            form.findChild(QtGui.QSpinBox, 'border_pad_v_val')
        ]


        self.form = form

        _default_val = [1, 1, 100, 100, 0, 0, 0, 0]
        _default_max = [100, 100, 1, 1, 50, 50, 98, 98]

        _callbacks = [
            self._onchange_dim_h, self._onchange_dim_v,
            self._onchange_size_h, self._onchange_size_v,
            self._onchange_pad_h, self._onchange_pad_v,
            self._onchange_border_h, self._onchange_border_v
        ]

        for _i, _v in enumerate(form.grid_params):
            _v.setMaximum(_default_max[_i])
            _v.setValue(_default_val[_i])
            _v.valueChanged.connect(_callbacks[_i])

        self.grid_tracker.update_border(0, 0)
        self.grid_tracker.update_dimension(1, 1)
        self.grid_tracker.update_pad(0, 0)
        self.grid_tracker.update_size(100, 100)

    def load_file(self, file_name = None):
        """
        Load the image file onto a plane
        """

        if not file_name:
            file_name = self.form.file_path.text()

        if self.plane:
            self.doc.removeObject(self.plane.Name)

        self.doc.recompute()

        self.image.load(file_name)

        self.cursor_trackers[0].update(
            [Vector(-50.0, 0.0, 0.0), Vector(50.0, 0.0, 0.0)]
        )

        self.cursor_trackers[1].update(
            [Vector(0.0, -50.0, 0.0), Vector(0.0, 50.0, 0.0)]
        )

        for _v in self.cursor_trackers:
            _v.set_selectability(False)
            _v.coin_style = CoinStyle.DASHED

        _plane = self.doc.addObject('Image::ImagePlane', 'SpriteSheet')
        _plane.ImageFile = file_name
        _plane.XSize = 100.0
        _plane.YSize = 100.0
        _plane.Placement = App.Placement()

        App.ActiveDocument.recompute()

        Gui.Selection.addSelection(_plane)

        Gui.SendMsgToActiveView('ViewFit')

        self.plane = _plane

    def choose_file(self):
        """
        Open the file picker dialog and open the file
        that the user chooses
        """

        open_path = resources.__path__[0]

        filters = self.form.tr(
            'All files (*.*);; PNG files (*.png);; JPG files (*.jpg)'
        )

        #selected_filter = self.form.tr('LandXML files (*.xml)')

        file_name = QtGui.QFileDialog.getOpenFileName(
            self.form, 'Select File', open_path, filters
        )

        if not file_name[0]:
            return

        self.form.file_path.setText(file_name[0])
        self.load_file(file_name[0])

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

    def key_event(self, arg):
        """
        SoKeyboardEvent callback
        """

        if arg['Key'] == 'ESCAPE':
            self.finish()

    def mouse_event(self, arg):
        """
        SoLocation2Event callback
        """

        if not self.plane:
            return

        MouseState().update(arg, ViewState().view.getCursorPos())

        #clear the matrix to force a refresh at the start of every mouse event
        ViewState().matrix = None

        if MouseState().object == self.plane.Name:

            self.cursor_trackers[0].update([
                Vector(-50.0, MouseState().coordinates.y, 0.0),
                Vector(50.0, MouseState().coordinates.y, 0.0)
            ])

            self.cursor_trackers[1].update([
                Vector(MouseState().coordinates.x, -50.0, 0.0),
                Vector(MouseState().coordinates.x, 50.0, 0.0)
            ])

        if MouseState().button1.dragging:

            if not DragState().node:
                self.start_drag()

            else:
                self.on_drag()

        elif DragState().node:
            self.end_drag()

    def start_drag(self):
        """
        Begin drag ops
        """

        DragState().node = self.rubberband_tracker.node
        DragState().add_node(self.rubberband_tracker.node)
        DragState().start = MouseState().coordinates

    def on_drag(self):
        """
        Continue drag ops
        """

        if MouseState().object != self.plane.Name:
            return

        self.rubberband_tracker.update()

    def end_drag(self):
        """
        Terminate drag ops
        """

        DragState().reset()

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        if not self.plane:
            return

        MouseState().update(arg, ViewState().view.getCursorPos())

        if MouseState().button1.state == 'UP':

            if DragState().node:
                self.end_drag()

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

        #re-enable selection
        ViewState().sg_root.getField("selectionRole").setValue(1)

        #close dialog
        Gui.Control.closeDialog()

        #remove the callback for action
        if self.callbacks:

            for _k, _v in self.callbacks.items():
                ViewState().view.removeEventCallback(_k, _v)

            self.callbacks.clear()


    #------------------------
    # SPINBOX CALLBACKS
    #------------------------

    def _onchange_border_h(self, arg):
        """Spinbox callback"""
        self.grid_tracker.update_border(horizontal = int(arg))

    def _onchange_border_v(self, arg):
        """Spinbox callback"""
        self.grid_tracker.update_border(vertical = int(arg))

    def _onchange_dim_h(self, arg):
        """Spinbox callback"""
        self.grid_tracker.update_dimension(horizontal = int(arg))

    def _onchange_dim_v(self, arg):
        """Spinbox callback"""
        self.grid_tracker.update_dimension(vertical = int(arg))

    def _onchange_size_h(self, arg):
        """Spinbox callback"""
        self.grid_tracker.update_size(horizontal = int(arg))

    def _onchange_size_v(self, arg):
        """Spinbox callback"""
        self.grid_tracker.update_size(vertical = int(arg))

    def _onchange_pad_h(self, arg):
        """Spinbox callback"""
        self.grid_tracker.update_pad(horizontal = int(arg))

    def _onchange_pad_v(self, arg):
        """Spinbox callback"""
        self.grid_tracker.update_pad(vertical = int(arg))
