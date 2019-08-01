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
import math

from FreeCAD import Vector
import FreeCADGui as Gui

import DraftTools

from .ff import FF
from ...support.mouse_state import MouseState
from ...support.view_state import ViewState

from ...trackers.grid_tracker import GridTracker

class GridTrackerTestTask:
    """
    Task to manage alignment editing
    """

    def __init__(self, doc):

        self.panel = None
        self.doc = doc
        self.grid_tracker = None

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

        self.grid_tracker = GridTestTracker(
            self.doc, 'Grid', self.alignment
        )

        DraftTools.redraw3DView()

    def _zoom_camera(self, use_bound_box=True):
        """
        Fancy routine to smooth zoom the camera
        """

        _camera = ViewState().view.getCameraNode()

        _start_pos = Vector(_camera.position.getValue().getValue())
        _start_ht = _camera.height.getValue()

        _center = Vector(self.camera_state['position'])
        _height = self.camera_state['height']

        if use_bound_box:

            _bound_box = self.camera_state['bound box']

            #get the center of the camera, setting the z coordinate positive
            _center = Vector(_bound_box.Center)
            _center.z = 1.0

            #calcualte the camera height = bounding box larger dim + 15%
            _height = _bound_box.XMax - _bound_box.XMin
            _dy = _bound_box.YMax - _bound_box.YMin

            if _dy > _height:
                _height = _dy

            _height += 0.15 * _height

        _frames = 60.0

        #calculate a total change value
        _pct_chg = abs(_height - _start_ht) / (_height + _start_ht)

        #at 50% change or more, use 60 frames,
        #otherwise scale frames to a minimum of 10 frames
        if _pct_chg < 0.5:
            _frames *= _pct_chg * 2.0

            if _frames < 10.0:
                _frames = 10.0

        #build cosine-based animation curve and reverse
        _steps = [
            math.cos((_i/_frames) * (math.pi/2.0)) * _frames\
                for _i in range(0, int(_frames))
        ]

        _steps = _steps[::-1]

        #calculate position and height deltas for transition loop
        _d_pos = _center - _start_pos
        _d_pos.multiply(1.0 / _frames)

        _d_ht = (_height - _start_ht) / _frames


        for _v in _steps:

            #set the camera
            ViewState().view.getCameraNode().position.setValue(
                tuple(_start_pos + (_d_pos * _v))
            )

            ViewState().view.getCameraNode().height.setValue(
                _start_ht + (_d_ht * _v)
            )

            Gui.updateGui()

    def setup(self):
        """
        Initiailze the task window and controls
        """

        pass
        #_mw = utils.getMainWindow()

        #form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        #self.form = form

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

        self.mouse.update(arg, ViewState().view.getCursorPos())

        #clear the matrix to force a refresh at the start of every mouse event
        ViewState().matrix = None

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        self.mouse.update(arg, ViewState().view.getCursorPos())

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

        if ViewState().view_objects:

            #reset line colors
            for _v in ViewState().view_objects['line_colors']:
                _v[0].LineColor = _v[1]

            #reenable object selctables
            for _v in ViewState().view_objects['selectable']:
                _v[0].Selectable = _v[1]

            ViewState().view_objects.clear()

        #re-enable selection
        ViewState().sg_root.getField("selectionRole").setValue(1)

        #close dialog
        Gui.Control.closeDialog()

        #remove the callback for action
        if self.callbacks:

            for _k, _v in self.callbacks.items():
                ViewState().view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        #delete the alignment object
        if self.alignment:
            self.doc.removeObject(self.alignment.Object.Name)
            self.alignment = None

        #shut down the tracker and re-select the object
        if self.pi_tracker:
            self.pi_tracker.finalize()
            self.pi_tracker = None
            Gui.Selection.addSelection(self.Object)

        if self.alignment_tracker:
            self.alignment_tracker.finalize()
            self.alignment_tracker = None

        if self.camera_state:
            self._zoom_camera(False)
