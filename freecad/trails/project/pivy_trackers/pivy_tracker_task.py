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

from pivy_trackers.trait.base import Base

from .pivy_tracker import PivyTracker

class PivyTrackerTask(Base):
    """
    Task to manage alignment editing
    """

    class BoundBox():
        """
        A simple bounding box class
        """

        def __init__(self, corners):
            """
            Constructor
            """

            self.x_min = corners[0]
            self.x_max = corners[2]
            self.y_min = corners[1]
            self.y_max = corners[3]

            self.center = (
                (corners[1] - corners[0]) / 2.0,
                (corners[3] - corners[2]) / 2.0,
                0.0
            )

        def __str__(self):
            return 'top: {}, left: {}, bottom: {}, right: {}, center: {}'\
                .format(
                    str(self.y_min), str(self.x_min),
                    str(self.y_max), str(self.x_max),
                    str(self.center)
                )

    class CameraState():
        """
        State tracker for camera
        """

        def __init__(self, position, height, box_corners):
            """
            Constructor
            position - tuple of three floats
            height - float
            box_corners - tuple of four floats for bounding box
                          (xmin, x_max, y_min, y_max)
            """

            self.position = position
            self.height = height
            self.bound_box = PivyTrackerTask.BoundBox(box_corners)

        def __str__(self):
            return 'position: {}\nheight: {}\nbox: {}\n'.format(
                str(self.position), str(self.height), str(self.bound_box)
            )

    def __init__(self):

        super().__init__('PivyTrackerTask', Gui.ActiveDocument.ActiveView)

        #self.panel = None

        _camera = self.view_state.view.getCameraNode()

        self.camera_state = self.CameraState(
            position=(0.0, 0.0, 0.0),
            height=0.0,
            box_corners=(-120.0, -120.0, 120.0, 120.0)
            )

        self.pivy_tracker = PivyTracker()
        self.pivy_tracker.insert_into_scenegraph(True)

        DraftTools.redraw3DView()

        self._zoom_camera()

    def _zoom_camera(self, use_bound_box=True):
        """
        Fancy routine to smooth zoom the camera
        """

        _camera = self.view_state.view.getCameraNode()

        _start_pos = Vector(_camera.position.getValue().getValue())
        _start_ht = _camera.height.getValue()

        _center = Vector(self.camera_state.position)
        _height = self.camera_state.height

        if use_bound_box:

            _bound_box = self.camera_state.bound_box

            #get the center of the camera, setting the z coordinate positive
            _center = Vector(_bound_box.center)
            _center.z = 1.0

            #calculate the camera height = bounding box larger dim + 15%
            _height = _bound_box.x_max - _bound_box.x_min
            _dy = _bound_box.y_max - _bound_box.y_min

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

        #close dialog
        Gui.Control.closeDialog()

        self.view_state.finish()

        if self.pivy_tracker:
            self.pivy_tracker.finalize()
            self.pivy_tracker = None

        if self.camera_state:
            self._zoom_camera(False)
