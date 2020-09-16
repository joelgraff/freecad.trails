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

from pivy_trackers.pivy_trackers.tracker.line_tracker import LineTracker
from pivy_trackers.pivy_trackers.tracker.polyline_tracker import PolyLineTracker

from ...geometry import arc, spiral, support

from pivy_trackers.pivy_trackers.coin import coin_utils

from collections.abc import Iterable
from freecad_python_support.tuple_math import TupleMath

from pivy_trackers.pivy_trackers.coin.coin_enums import NodeTypes as Nodes
from pivy_trackers.pivy_trackers.coin.coin_styles import CoinStyles
from pivy_trackers.pivy_trackers.coin.todo import todo

from pivy_trackers.pivy_trackers.tracker.marker_tracker import MarkerTracker
from pivy_trackers.pivy_trackers.tracker.geometry_tracker import GeometryTracker
from pivy_trackers.pivy_trackers.tracker.context_tracker import ContextTracker

from pivy_trackers.pivy_trackers.trait.drag import Drag
from pivy_trackers.pivy_trackers.trait.style import Style

class CurveTracker(ContextTracker, Style, Drag):
    """
    Tracker object for managing curves
    """

    def __init__(self, name, curve, parent, view=None):
        """
        Constructor
        """

        #generate line tracker structures from the pi list

        super().__init__(name=name, parent=parent, view=view)

        self.curve_tracker = None
        self.param_tracker = None
        self.arc = None

        self.build_trackers(parent, curve)

        self.set_visibility()

        self.last_rebuild = None

    def build_trackers(self, parent, curve):
        """
        Generate trackers based on the passed point list
        """
        _name = self.name

        if not curve.curve_type:
            _name += curve.type

        self.arc = curve
        self.arc.points = arc.get_points(self.arc, _dtype=tuple)

        self.param_tracker = PolyLineTracker(
            _name + '_radius',
            [tuple(curve.start), tuple(curve.center), tuple(curve.end)],
            self.base
            )

        self.c_tracker =\
            LineTracker(_name + '_CURVE ', curve.points, self.base)

        self.c_tracker.set_visibility()

        _n = ['start', 'center', 'end']
        _f = [self.on_endpoint_drag, self.on_centerpoint_drag]
        _i = 0

        for _l in self.param_tracker.lines:

            for _m in _l.markers:

                _m.name = _m.name + '_' + '_n[_i]'
                _i += 1

        self.param_tracker.set_visibility()

    def on_endpoint_drag(self, user_data):
        """
        Update the curve and marker position when an endpoint is dragged
        """

    def on_centerpoint_drag(self, user_data):
        """
        Update the curve and marker position when the centerpoint is dragged
        """

    def find_geometry(self, name):
        """
        Find the geometry specified by name
        """
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

    def set_pi(self, pi):
        """
        Set the arc pi
        """

        self.arc.pi = pi

    def set_bearings(self, bearing_in=None, bearing_out=None):
        """
        Set the curve bearings for the next recalculation
        """

        if bearing_in is None:
            bearing_in = self.arc.bearing_in

        if bearing_out is None:
            bearing_out = self.arc.bearing_out

        _arc = arc.Arc()
        _arc.bearing_in = bearing_in
        _arc.bearing_out = bearing_out
        _arc.radius = self.arc.radius
        _arc.direction = self.arc.direction
        _arc.pi = self.arc.pi

        self.arc = arc.Arc(arc.get_parameters(_arc))

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

    def update(self, arc_obj=None):
        """
        Override of Geometry method
        """

        if not arc_obj:
            arc_obj = self.arc
        else:
            self.arc = arc.Arc(arc.get_parameters(arc_obj))

        if not all([self.arc.start, self.arc.end, self.arc.center]):
            self.arc = arc.Arc(arc.get_parameters(arc_obj))

        _points = arc.get_points(self.arc, _dtype=tuple)

        #update the drag copy if in the middle of drag ops
        if self.drag_copy:
            _coordinate = self.drag_copy.getChild(0).getChild(2).getChild(1)
            _coordinate.point.setValues(_points)

        else:

            self.c_tracker.update(_points)

            _pts = [
                tuple(self.arc.start), tuple(self.arc.center), tuple(self.arc.end)]

            self.param_tracker.update(_pts)

    def _update_text(self):
        """
        Update curve-specific text
        """

        self.text.set_translation(
            TupleMath.mean(self.coordinates)
        )

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

        #abort as the drag has alredy been set up.
        if self.drag_copy:
            return

        self.drag_copy = self.base.copy().getChild(0).getChild(5)
        Drag.drag_tracker.insert_no_drag(self.drag_copy)

        Drag.drag_tracker.set_constraint_geometry(axis=(0.0, 1.0, 0.0))

        draw = self.drag_copy.getChild(0).getChild(1).getChild(0)
        color = self.drag_copy.getChild(0).getChild(1).getChild(1)

        style = CoinStyles.DASHED
        style.color = CoinStyles.Color.BLUE

        draw.lineWidth = style.line_width
        draw.style = style.style
        draw.linePattern = style.line_pattern

        color.rgb = style.color

    def on_drag(self, user_data):
        """
        During drag operations
        """

        #super().on_drag(user_data)

    def after_drag(self, user_data):
        """
        End-of-drag operations
        """

        self.text_copies = []
        self.drag_copy = None
        print(self.name, 'after_drag')
        #super().after_drag(user_data)

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
