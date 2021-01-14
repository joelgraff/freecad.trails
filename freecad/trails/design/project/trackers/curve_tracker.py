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

import math
from types import SimpleNamespace

from pivy_trackers.tracker.line_tracker import LineTracker
from pivy_trackers.tracker.polyline_tracker import PolyLineTracker

from ...geometry import arc

from freecad_python_support.tuple_math import TupleMath

from pivy_trackers.coin.coin_styles import CoinStyles as Styles

from pivy_trackers.tracker.context_tracker import ContextTracker

from pivy_trackers.trait.drag import Drag
from pivy_trackers.trait.style import Style

class CurveTracker(ContextTracker, Style, Drag):
    """
    Tracker object for managing curves
    """

    def __init__(self, name, curve, parent, view=None):
        """
        Constructor
        """

        #generate line tracker structures from the pi list

        if not name:
            name = 'CURVE_TRACKER'

        super().__init__(name=name, parent=parent, view=view)

        self.curve_tracker = None
        self.param_tracker = None
        self.arc = None
        self.axes = [(), (), ()]

        self.drag_start_point = None
        self.drag_axis = None
        self.is_invalid = False

        self.build_trackers(parent, curve)

        self.set_visibility()

        self.last_rebuild = None

    def build_trackers(self, parent, curve):
        """
        Generate trackers based on the passed point list
        """
        _name = self.name

        self.arc = curve
        self.arc.points = arc.get_points(self.arc, _dtype=tuple)

        self.param_tracker = PolyLineTracker(
            _name + '_radius',
            [tuple(curve.start), tuple(curve.center), tuple(curve.end)],
            self.base, is_adjustable=False)

        _line_names = ['start_radius', 'end_radius']
        _point_names = ['start', 'center', 'end']

        _j = 0

        for _i, _l in enumerate(self.param_tracker.lines):

            _l.update_after_drag = False
            _l.name = self.name + "_" + _line_names[_i]

            for _m in _l.markers:

                _m.update_after_drag = False
                _m.name = self.name + "_" + _point_names[_j]
                _j += 1

        self.c_tracker =\
            LineTracker(_name + '_arc ', curve.points, self.base)

        self.c_tracker.update_after_drag = False
        self.c_tracker.is_draggable = False

        #build list of all trackers and append curve callbacks to them
        _t = [self.c_tracker]

        for _l in self.param_tracker.lines:
            _t.append(_l)

            for _m in _l.markers:
                _t.append(_m)

        for _v in _t:

            _v.before_drag_callbacks.append(self.before_drag)
            _v.on_drag_callbacks.append(self.on_drag)
            _v.after_drag_callbacks.append(self.after_drag)

        self.param_tracker.set_visibility()

    def after_drag(self, user_data):
        """
        End-of-drag operations
        """

        self.text_copies = []
        self.drag_copy = None
        self.drag_start_point = None
        self.is_inavlid = False

        self.update()

    def on_drag(self, user_data):

        _xlate = user_data.matrix.getValue()[3]
        _point = Drag.drag_tracker.drag_position

        for _v in ['start', 'center', 'end']:

            if _v in user_data.obj.name:

                self.arc.set(_v, _point)

            elif _v == 'center' and 'arc' in user_data.obj.name:

                if self.drag_axis:
                    _xlate = TupleMath.project(_xlate[0:3], self.drag_axis)

                self.arc.set(_v, TupleMath.add(self.drag_start_point, _xlate))

            else:
                self.arc.set(_v, None)

        self.arc.radius = None
        self.arc.tangent = None

        self.update()

        for _cb in self.on_drag_callbacks:
            _cb(user_data)

    def before_drag(self, user_data):
        """
        Start of drag operations
        """

        #abort as the drag has alredy been set up.
        if self.drag_copy:
            return

        self.setup_drag_tracker_geometry()
        self.setup_drag_references(user_data.obj.name)

        #if this object is the object directly picked, set the drag center
        #if self.name == user_data.obj.name:
        #    user_data.obj.drag_center = self.drag_center

    def setup_drag_references(self, nam):
        """
        Set parameters to be referenced during on_drag operations
        """

        _drag_ctr = self.arc.start
        _bearing = self.arc.bearing_in
        _origin = None

        if 'center' in nam or 'arc' in nam:

            _drag_ctr = self.arc.center
            _bearing = TupleMath.bearing(
                TupleMath.subtract(tuple(self.arc.pi), tuple(self.arc.center))
            )

            if 'arc' in nam:

                _l = len(self.arc.points)
                _l_2 = int(_l / 2)
                _drag_ctr = self.arc.points[_l_2 - 1]

                if (_l % 2):
                    _drag_ctr = TupleMath.mean(_drag_ctr, self.arc.points[_l_2])
                _drag_ctr = self.arc.center
                self.drag_start_point = self.arc.center
                _origin = self.arc.center

        elif 'end' in nam:

            _drag_ctr = self.arc.end
            _bearing = self.arc.bearing_out

        self.drag_center = _drag_ctr

        if not _origin:
            _origin = _drag_ctr

        #generate constraint geometry along an axis defined by the bearing
        while _bearing > math.pi:
            _bearing -= math.pi

        self.drag_axis = (1.0, 1.0 /    math.tan(_bearing), 0.0)
        Drag.drag_tracker.set_constraint_geometry(self.drag_axis,_origin)

    def setup_drag_tracker_geometry(self):
        """
        Set up the geometry to be represented in the dragging operation
        """

        #build the drag copy data structure
        self.drag_copy = SimpleNamespace(
            draw_list=[], color_list=[],
            marker_coords=[], line_coords=[], curve_coord=None)

        #get the key graph nodes
        _start = self.base.get_child(

        #_curve = self.base.get_child(_start, f'{self.name}_arc_BASE_Switch')

        return

        _polyline = _start.getChild(4)

        #add the root node to the drag tracker for representation only
        Drag.drag_tracker.insert_no_drag(_start)

        #append the styling nodes
        self.drag_copy.draw_list.append(
            _curve.getChild(0).getChild(1).getChild(0))

        self.drag_copy.color_list.append(
            _curve.getChild(0).getChild(1).getChild(1))

        #get the curve coordinate node
        self.drag_copy.curve_coord = _curve.getChild(0).getChild(2).getChild(1)

        #get style and coordinate nodes for the markers and lines
        for _i in (0, 1, 2, 9, 10):

            _base = _polyline.getChild(0).getChild(_i).getChild(0)

            self.drag_copy.draw_list.append(_base.getChild(1).getChild(0))
            self.drag_copy.color_list.append(_base.getChild(1).getChild(1))

            _node = _base.getChild(2).getChild(1)

            if _i < 9:
                self.drag_copy.marker_coords.append(_node)

            else:
                self.drag_copy.line_coords.append(_node)

        #set the default styles
        style = Styles.DASHED
        style.color = Styles.Color.BLUE

        for _d in self.drag_copy.draw_list:

            _d.lineWidth = style.line_width
            _d.style = style.style
            _d.linePattern = style.line_pattern

        for _c in self.drag_copy.color_list:
            _c.rgb = style.color

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

    def update(self, arc_obj=None, notify=True):
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

            _coordinate = self.drag_copy.curve_coord
            _coordinate.point.setValues(_points)

            _pts = (    tuple(self.arc.start),
                        tuple(self.arc.center),
                        tuple(self.arc.end)
                    )

            for _i, _c in enumerate(self.drag_copy.line_coords):
                _c.point.setValues((_pts[_i], _pts[_i + 1]))

            _color = Styles.Color.BLUE

            if self.is_invalid:
                _color = Styles.Color.RED

            for _s in self.drag_copy.color_list:
                _s.rgb = _color

        else:

            self.c_tracker.update(arc_obj.points, notify='10')

            _pts = [
                tuple(self.arc.start), tuple(self.arc.center), tuple(self.arc.end)]

            self.param_tracker.update(_pts)

            #_geo = self.top.getChild(5).getChild(0).getChild(2)
            #todo.delay(self.base.dump, _geo)

            #_fn = lambda x: print(self.view_state.get_matrix(x).getValue())
            #todo.delay(_fn, _geo.getChild(1))

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
        self.is_invalid = False

        super().finish()
