# -*- coding: utf-8 -*-
#***********************************************************************
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
Curve tracker class for tracker objects
"""

from pivy_trackers.tracker.line_tracker import LineTracker

from ...geometry import arc, spiral, support

from pivy_trackers.coin import coin_utils

from collections.abc import Iterable
#from ..support.tuple_math import TupleMath

from pivy_trackers.coin.coin_enums import NodeTypes as Nodes
from pivy_trackers.coin.todo import todo

from pivy_trackers.tracker.marker_tracker import MarkerTracker
from pivy_trackers.tracker.context_tracker import ContextTracker

print('IMPORT CURVE_TRACKER')
class CurveTracker(ContextTracker):
    """
    Tracker object for managing curves
    """

    def __init__(self, name, curve, pi_list, parent, view=None):
        """
        Constructor
        """

        #generate line tracker structures from the pi list

        super().__init__(name=name, parent=parent, view=view)

        self.trackers = self.build_trackers(curve, pi_list)

    def build_trackers(self, curve, pi_list):
        """
        Generate trackers based on the passed point list
        """

        for _k, _v in curve.__dict__.items():
            print(_k, '\t', _v)

        _name = self.name

        if not curve.curve_type:
            _name += curve.type

        self.arc_tracker = LineTracker(_name, curve.points, self.base)

        return

        #nodes
        _labels = ['Start', 'Center', 'End']
        _points = [self.curve.get(_k) for _k in _labels]

        for _i, _v in enumerate(_points):

            _nt = NodeTracker(
                names[:2] + [self.name + '-' + _labels[_i]], _v
            )

            _nt.set_visibility(False)
            _nt.state.multi_select = False
            _nt.show_drag_line = False

            _nt.update()

            self.node_trackers.append(_nt)

            _nt.register(self, [Events.NODE.UPDATED, Events.NODE.SELECTED])

        #radius wire
        self.wire_tracker = WireTracker(names[:2] + [self.name + '-Radius'])

        self.wire_tracker.set_points(nodes=self.node_trackers)
        self.wire_tracker.set_selectability(False)
        self.wire_tracker.set_visibility(False)
        self.wire_tracker.update()

    def get_length(self):
        """
        Return the curve length
        """

    def set_length(self, length):
        """
        Set the length of the curve
        """

        super().set_length(length)

    def get_radius(self):
        """
        Return the curve radius
        """

    def set_radius(self):
        """
        Set the curve radius
        """

    def show_markers(self):
        """
        Show the SoMarkerSet
        """

        self.markers.set_visibility(True)

    def hide_markers(self):
        """
        hide the SoMarkerSet
        """

        self.markers.set_visibility(False)

    def set_vertex_groups(self, groups):
        """
        Set the vertex groups for the line tracker

        groups - an itearable of vertex groupings
        """

        assert(sum(groups) == len(self.pionts)),\
            'LineTracker.set_vertex_groups: group count does not match number of points'

        self.line.numVertices.setValues(0, len(groups), groups)

    def update(self, coordinates=None, matrix=None, groups=None, notify=True):
        """
        Override of Geometry method
        """

        super().update(coordinates=coordinates, matrix=matrix, notify=notify)

        if self.text and self.text.is_visible():

            self.text.set_translation(
                TupleMath.mean(self.coordinates)
            )

        if self.update_cb:
            self.update_cb()

        if groups:
            self.groups = groups
            self.line.numVertices.setValues(0, len(groups), groups)

        if self.coordinates:
            self.center = TupleMath.mean(self.coordinates)

        self.text_center = self.center
        self.set_text_translation((0.0, 0.0, 0.0))

    def drag_text_update(self, text):
        """
        Update the drag text.  Called from inheriting class
        """

        #directly update the text of the node in the drag copy
        #with the supplied string

        for _v in self.text_copies:
            self.set_text(text, _v)

    def before_drag(self, user_data):
        """
        Start of drag operations
        """

        super().before_drag(user_data)

    def on_drag(self, user_data):
        """
        During drag operations
        """

        super().on_drag(user_data)

    def after_drag(self, user_data):
        """
        End-of-drag operations
        """

        self.text_copies = []
        super().after_drag(user_data)

    def drag_mouse_event(self, user_data, event_cb):
        """
        Override of Drag.drag_mouse_event()
        """

        self.set_drag_axis(self.drag_axis)
        super().drag_mouse_event(user_data, event_cb)

    def link_marker(self, marker, index):
        """
        Link a marker node to the line for automatic updates
        """

        self.link_geometry(marker, index, 0)

    def update_drag_center(self):
        """
        Override of Drag method
        """

        #default to the current cursor position
        _pt = self.mouse_state.world_position

        #average the coordinates to calculate the centerpoint
        if self.drag_style == self.DragStyle.AVERAGE:

            _pt = (0.0, 0.0, 0.0)

            for _p in self.coordinates:
                _pt = TupleMath.add(_pt, _p)

            _pt = TupleMath.multiply(_pt, 0.5)

        #use Manhattan distance to find nearest endpoint
        elif self.drag_style == self.DragStyle.ENDPOINT:

            _dist = -1
            _cursor = self.mouse_state.world_position
            _pt = _cursor

            _fn = lambda p1, p2: abs(_pt[0] - _p[0])\
                        + abs(_pt[1] - _p[1])\
                        + abs(_pt[2 - _p[2]])

            for _p in self.coordinates:

                if _dist == -1:
                    _dist = _fn(_cursor, _p)
                    continue

                _new_dist = _fn(_cursor, _p)

                if _new_dist < _dist:
                    _dist = _new_dist
                    _pt = _p

        return _pt

    def reset(self):
        """
        Reset geometry
        """

        self.line.numVertices.setValues(0,0,[])
        self.line.numVertices.touch()
        super().reset()

    def finish(self):
        """
        Cleanup
        """

        self.line = None
        self.drag_style = None
        self.linked_geometry = None

        super().finish()
