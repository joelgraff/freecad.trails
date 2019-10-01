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

from ....alignment import alignment

from ...support import const

from ...trackers2.tracker_tester import TrackerTester

from ...trackers2.support.view_state import ViewState
from ...trackers2.support.mouse_state import MouseState
from ...trackers2.support.smart_tuple import SmartTuple

def create(doc, alignment_data, object_name, is_linked):
    """
    Class factory method
    """

    return BaseTrackerTestTask(doc, alignment_data, object_name, is_linked)

class BaseTrackerTestTask():
    """
    Task to manage alignment editing
    """

    view_state = ViewState()

    @staticmethod
    def set_vobj_style(vobj, style):
        """
        Set the view object style based on the passed style tuple
        """

        vobj.LineColor = style[0]
        vobj.DrawStyle = style[1]

    class STYLES(const.Const):
        """
        Internal constants used to define ViewObject styles
        """

        DISABLED = [(0.4, 0.4, 0.4), 'Solid']
        ENABLED = [(0.8, 0.8, 0.8), 'Solid']
        HIGHLIGHT = [(0.0, 1.0, 0.0), 'Solid']
        PI = [(0.0, 0.0, 1.0), 'Solid']
        SELECTED = [(1.0, 0.8, 0.0), 'Solid']

    def __init__(self, doc, alignment_data, obj, is_linked):


        super().__init__()
        #    '.'.join([doc.Name, 'BASE_TRACKER_TEST_TASK', 'TASK']))

        self.panel = None
        self.doc = doc
        self.Object = obj
        self.alignment = alignment.create(alignment_data, 'TEMP', True, False)
        self.pi_tracker = None
        self.drag_tracker = None
        self.alignment_tracker = None
        self.callbacks = {}

        self.camera_state = {
            'position': None,
            'height': None,
            'bound box': None
        }

        self.view_state.view_objects = {
            'selectables': [],
            'line_colors': [],
        }

        #disable selection entirely
        self.view_state.sg_root.getField("selectionRole").setValue(0)

        #get all objects with LineColor and set them all to gray
        self.view_state.view_objects['line_colors'] = [
            (_v.ViewObject, _v.ViewObject.LineColor)
            for _v in self.doc.findObjects()
            if hasattr(_v, 'ViewObject')
            if hasattr(_v.ViewObject, 'LineColor')
        ]

        for _v in  self.view_state.view_objects['line_colors']:
            self.set_vobj_style(_v[0], self.STYLES.DISABLED)

        #get all objects in the scene that are selectable.
        self.view_state.view_objects['selectable'] = [
            (_v.ViewObject, _v.ViewObject.Selectable)
            for _v in self.doc.findObjects()
            if hasattr(_v, 'ViewObject')
            if hasattr(_v.ViewObject, 'Selectable')
        ]

        for _v in  self.view_state.view_objects['selectable']:
            _v[0].Selectable = False

        #deselect existing selections
        Gui.Selection.clearSelection()

        self.alignment_tracker = TrackerTester(
            self.doc, self.Object.Name, self.alignment, is_linked
        )

        #save camera state
        _camera = self.view_state.view.getCameraNode()

        self.camera_state['position'] = _camera.position.getValue().getValue()
        self.camera_state['height'] = _camera.height.getValue()
        self.camera_state['bound box'] = self.Object.Shape.BoundBox

        #add mouse callbacks for updating mouse state
        ViewState().add_mouse_event(self.mouse_event)
        ViewState().add_button_event(self.button_event)

        self._zoom_camera()

        DraftTools.redraw3DView()

    def _zoom_camera(self, use_bound_box=True):
        """
        Fancy routine to smooth zoom the camera
        """

        _camera = self.view_state.view.getCameraNode()

        _start_pos = Vector(_camera.position.getValue().getValue())
        _start_ht = _camera.height.getValue()

        _center = Vector(self.camera_state['position'])
        _height = self.camera_state['height']

        if use_bound_box:

            _bound_box = self.camera_state['bound box']

            #get the center of the camera, setting the z coordinate positive
            _center = Vector(_bound_box.Center)
            _center.z = 1.0

            #calculate the camera height = bounding box larger dim + 15%
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
            self.view_state.view.getCameraNode().position.setValue(
                tuple(_start_pos + (_d_pos * _v))
            )

            self.view_state.view.getCameraNode().height.setValue(
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
        ViewState mouse event
        """

        _last_pos = SmartTuple(MouseState().world_position)

        MouseState().update(arg, self.view_state)

        if not (MouseState().shift_down and _last_pos._tuple\
            and MouseState().vector.Length):

            return

        _vec = SmartTuple(MouseState().vector).normalize(0.10)
        _new_pos = _last_pos.add(_vec)._tuple

        MouseState().set_mouse_position(self.view_state, _new_pos)

    def button_event(self, arg):
        """
        ViewState button event
        """

        MouseState().update(arg, self.view_state)

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

        if self.view_state.view_objects:

            #reset line colors
            for _v in self.view_state.view_objects['line_colors']:
                _v[0].LineColor = _v[1]

            #re-enable object selectables
            for _v in self.view_state.view_objects['selectable']:
                _v[0].Selectable = _v[1]

            self.view_state.view_objects.clear()

        #re-enable selection
        self.view_state.sg_root.getField("selectionRole").setValue(1)

        #close dialog
        Gui.Control.closeDialog()

        self.view_state.finish()

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
