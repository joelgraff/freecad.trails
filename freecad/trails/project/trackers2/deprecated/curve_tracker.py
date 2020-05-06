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
Tracker for curve editing
"""
import math

from FreeCAD import Vector

from ...geometry import arc, spiral, support

from ..support.mouse_state import MouseState
from ..support.drag_state import DragState
from ..support.select_state import SelectState
from ..support.view_state import ViewState
from ..support.publisher import PublisherEvents as Events

from .node_tracker import NodeTracker
from .wire_tracker import WireTracker
from .trait.coin.coin_styles import CoinStyles

class CurveTracker(WireTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, names, curve, pi_nodes):
        """
        Constructor
        """

        super().__init__(names=names)

        if curve['Type'] == 'Curve':
            curve = arc.Arc(curve)

        self.curve = curve
        self.pi_nodes = pi_nodes
        self.is_valid = True
        self.drag_curve = None
        self.drag_style = None
        self.drag_color = None
        self.drag_last_mouse = None
        self.drag_curve_middle = None
        self.external_select = False
        self.pt_attr_pairs = [
            ('Start', 'Tangent'),
            ('End', 'Tangent'),
            ('Center', 'Middle'),
            ('Curve', 'External')
        ]

        self.event_type = Events.CURVE.EVENTS

        #connect the curve to it's PI nodes to manage updates
        for _v in self.pi_nodes:
            _v.register(self, [Events.NODE.UPDATED, Events.NODE.SELECTED])

        self.pt_labels = ['Start', 'Center', 'End']

        self.update_curve()

        self.wire_tracker = None
        self.node_trackers = []

        self.build_trackers(names)

        self.insert_node(self.wire_tracker.switch, self.get_node())

        for _v in self.node_trackers:
            self.insert_node(_v.switch, self.get_node(), 0)

        self.state.multi_select = False

    def mouse_event(self, arg):
        """
        Override base event
        """

        #internal tracker visiblity criteria:
        # 1. curve must be the mouse component
        # 2. selection state must be manual

        #manual selection indicates curve is picked.
        #this is for mouse-over only
        if self.is_selected() != 'MANUAL':
            self._set_internal_visiblity(self.name in MouseState().component)

        super().mouse_event(arg)

    def button_event(self, arg):
        """
        Override base event
        """

        self._handle_external_select()

        if not self.external_select:

            self._handle_internal_select()
            super().button_event(arg)

            self._set_internal_visiblity(self.is_selected() != '')

        else:
            self._set_internal_visiblity(False)

        if MouseState().button1.state == 'UP':

            self.update_dragging()
            self.update_highlighting()

        elif self.pi_nodes[1].is_selected():
            self.dispatch(Events.CURVE.SELECTED, (self.name, self.curve))

        self.refresh()

    def notify(self, event, message):
        """
        Base implementation override
        """

        return
        super().notify(event, message)

        if event == Events.NODE.UPDATED:

            self.drag_curve = self._generate_external_arc()
            self.update_curve(self.drag_curve, temporary=True)
            #self.dispatch(
            #    Events.CURVE.UPDATED, (self.name, self.drag_curve), False)

        elif event == Events.CURVE.UPDATE:

            if self.is_valid and self.drag_curve:
                self.curve = self.drag_curve
                self.drag_curve = None

            self.update_curve()

    def _set_internal_visiblity(self, is_visible):
        """
        Set the visiblity of the internal curve geometry
        """

        self.wire_tracker.set_visibility(is_visible)

        for _v in self.node_trackers:
            _v.set_visibility(is_visible)

    def _handle_internal_select(self):
        """
        Manage selection for graphical curve editing.
        """

        if not self.name in MouseState().component and self.is_selected():
            SelectState().deselect(self)

        #selection based on any node, the wire, or the object itself is picked
        _selected = self.is_selected()\
            or self.wire_tracker.is_selected()\
            or any([_v.is_selected() for _v in self.node_trackers])\
            or self.name in MouseState().component

        if not _selected:
            return

        #manually select the trackers, this is an internal selection operation
        SelectState().clear_state()

        SelectState().manual_select(self)
        SelectState().manual_select(self.wire_tracker)
        self.wire_tracker.refresh()

        for _v in self.node_trackers:
            SelectState().manual_select(_v)

    def _handle_external_select(self):
        """
        Manage selection if PI nodes are clicked
        """

        if MouseState().button1.state == 'UP':
            return

        self.external_select = False

        #after setting value to false, return if the curve is selected
        if self.name in MouseState().component:
            return

        #this test must perform on both button down and button up to
        #catch late node selections
        _pi_select = [_v for _v in self.pi_nodes if _v.is_selected()]

        #if a PI node is selected treat as an external selection
        if _pi_select:

            self.external_select = True

            #Full-select the curve if all three PI nodes are picked
            #because the curve can be transformed with the drag state nodes
            if len(_pi_select) == 3 and self.is_selected != 'FULL':
                SelectState().select(self, force=True)

            #manual selection if any PI nodes are not picked, because
            #the curve will have to be updated separately during dragging
            elif self.is_selected() != 'MANUAL':
                SelectState().manual_select(self)

        elif not MouseState().component:

            SelectState().deselect(self.wire_tracker)

            for _v in self.node_trackers:
                SelectState().deselect(_v)

            SelectState().deselect(self)

    def start_drag(self):
        """
        Override base implementation
        """

        return
        if not self.is_selected():
            return

        super().start_drag()

        #reference the SoDrawStyle and SoBaseColor nodes of copied drag nodes
        self.drag_style = self.drag_copy.getChild(1)
        self.drag_color = self.drag_copy.getChild(2)

        self.event_type = Events.CURVE.UPDATED

        #abort if PI nodes are being dragged
        if self.external_select:

            self.set_style(style=CoinStyles.SELECTED,
                           draw=self.drag_copy.getChild(1),
                           color=self.drag_copy.getChild(2))

            return

        #disable drag state translations since curve editing requires
        #manual updates
        DragState().update_translate = False

        self.drag_curve_middle = math.floor((len(self.curve.points) - 1) / 2)

        DragState().start = self.curve.points[self.drag_curve_middle]

        if self.external_select and self.pi_nodes[1].is_selected():
            self.dispatch(self.event_type, (self.name, self.curve), False)

    def on_drag(self):
        """
        Override base implementation
        """

        return
        if self.select_state != 'MANUAL':
            return

        if not self.state.dragging and self != DragState().drag_node:
            return

        #external changes (PI nodes) only
        if self.external_select:
            return

        #internal drag state update
        #self._update_drag_state()

    def _update_drag_state(self):
        """
        Update the curve drag state during drag ops
        """

        #all movements are constrained to  a line and update a single
        #curve attribute
        _pair = ['Center', 'External']

        #determine which point is being dragged (center / curve is default)
        for _k in self.pt_attr_pairs:
            if _k[0] in MouseState().component:
                _pair = _k

        #update DragState
        DragState().translate(MouseState().coordinates)
        DragState().coordinates = MouseState().coordinates

        #regenerate the curve and points
        self.drag_curve = \
            self._generate_internal_arc(attr=_pair[1], point=_pair[0])

        _pts = arc.get_points(self.drag_curve, _dtype=tuple)

        #update the curve drag geometry in the manual drag group
        if self.drag_copy:
            _node = self.drag_copy.getChild(3).point
            _node.setValues(0, len(_pts), _pts)

            self._update_drag_trackers(_pts)

        self._update_drag_line(_pair[0])

    def _update_drag_trackers(self, points):
        """
        Update the tracker geometry copied to DragState()
        """

        #update tracker drag geometry
        _pts = [points[0], tuple(self.drag_curve.center), points[-1]]

        for _v in self.node_trackers:

            _point = _v.drag_copy.getChild(3).point

            if 'Start' in _v.name:
                _point.setValue(_pts[0])

            elif 'Center' in _v.name:
                _point.setValue(_pts[1])

            else:
                _point.setValue(_pts[2])

        self.wire_tracker.drag_copy.getChild(3).point.setValues(0, 3, _pts)

    def _update_drag_line(self, drag_point):
        """
        Update the drag line during drag ops
        """

        #update the drag state to reflect movement along curve's central axis
        #default to start node selection
        _drag_line_start = Vector(DragState().start)
        _drag_line_end = Vector(self.drag_curve.points[0])

        #project the drag line end to a tangent or the middle vector
        if drag_point == 'End':
            _drag_line_end = self.drag_curve.points[-1]

        elif drag_point == 'Center':

            _drag_line_end = self.curve.pi.add(
                self.project_to_line(
                    self.curve.pi, _drag_line_start, MouseState().coordinates)
            )

        elif drag_point == 'Curve':
            _drag_line_end =\
                Vector(self.drag_curve.points[self.drag_curve_middle])

        DragState().update(_drag_line_start, _drag_line_end)

    def end_drag(self):
        """
        Override base function
        """

        return
        super().end_drag()

        if not DragState().abort:

            if self.drag_curve:
                self.curve = self.drag_curve

            _points = [
                self.curve.start, self.curve.center, self.curve.end,
                self.curve.pi
            ]

            if not self.drag_curve:
                _points = ViewState().transform_points(_points)

            _curve = arc.Arc(self.curve)
            _curve.start = Vector(_points[0])
            _curve.center = Vector(_points[1])
            _curve.end = Vector(_points[2])
            _curve.pi = Vector(_points[3])

            _curve = arc.get_parameters(_curve, False)

            self.curve = _curve

            for _i, _v in enumerate(self.node_trackers):
                _v.update(_points[_i])
                _v.refresh()

            self.wire_tracker.update(_points)

        if self.external_select and self.pi_nodes[1].is_selected():
            self.dispatch(self.event_type, (self.name, self.curve), False)

        self.drag_curve = None
        self.drag_style = None
        self.drag_color = None
        self.state.dragging = False
        self.is_valid = True
        self.drag_curve_middle = 0.0
        self.external_select = False

    def build_trackers(self, names):
        """
        Create the radius tracker for curve editing

        """

        #nodes
        _points = [self.curve.get(_k) for _k in self.pt_labels]

        for _i, _v in enumerate(_points):

            _nt = NodeTracker(
                names[:2] + [self.name + '-' + self.pt_labels[_i]], _v
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

    def update_curve(self, curve=None, temporary=False):
        """
        Update the curve based on the passed data points
        curve - Arc to update curve.  If omitted, self.curveis used
        temporary - Update wire based on curve, but do not assign self.curve
        """

        if not self.is_valid:
            return

        if curve is None:
            curve = self.curve

        _points = None

        if curve.type == 'Spiral':
            _points = self._generate_spiral()

        else:
            arc.get_points(curve)

        if not _points and not curve.points:
            return

        super().update(curve.points)

        if not temporary:
            self.curve = curve

    def _generate_spiral(self, is_dragging=False):
        """
        Generate a spiral curve
        """

        _key = ''

        _start = Vector(self.pi_nodes[0].point)
        _pi = Vector(self.pi_nodes[1].point)
        _end = Vector(self.pi_nodes[2].point)

        if not self.curve.get('StartRadius') \
            or self.curve['StartRadius'] == math.inf:

            _key = 'EndRadius'
            _end = self.curve['End']

            #first curve uses the start point.
            #otherwise, calculate a point halfway in between.
            if _start.is_end_node:

                _start = _pi.sub(
                    Vector(_pi.sub(_start)).multiply(
                        _start.distanceToPoint(_pi) / 2.0
                    )
                )

        else:

            _key = 'StartRadius'
            _start = self.curve['Start']

            #last curve uses the end point.
            #otherwise, calculate a point halfway between.
            if _start.is_end_node:

                _end = _pi.add(
                    Vector(_end.sub(_pi)).multiply(
                        _end.distanceToPoint(_pi) / 2.0)
                )

        _curve = {
            'PI': _pi,
            'Start': _start,
            'End': _end,
            _key: self.curve[_key]
        }

        _curve = spiral.solve_unk_length(_curve)

        #re-render the last known good points if an error occurs
        if _curve['TanShort'] <= 0.0 or _curve['TanLong'] <= 0.0:
            _curve = self.curve

        self.curve = _curve

        return spiral.get_points(self.curve)

    @staticmethod
    def project_to_line(line_start, line_end, coord):
        """
        Project a coordinate to the specified line
        """

        _line_vec = line_end.sub(line_start)
        _coord_vec = coord.sub(line_start)
        _proj = Vector().projectToLine(_coord_vec, _line_vec)

        return _coord_vec.add(_proj)


    def _generate_external_arc(self):
        """
        Generate the arc based on changes to the PI nodes
        """

        _curve = arc.Arc()

        _curve.bearing_in =\
            support.get_bearing(
                Vector(self.pi_nodes[1].drag_point).sub(
                    Vector(self.pi_nodes[0].drag_point))
            )

        _curve.bearing_out =\
            support.get_bearing(
                Vector(self.pi_nodes[2].drag_point).sub(
                    Vector(self.pi_nodes[1].drag_point))
            )

        _curve.pi = Vector(self.pi_nodes[1].drag_point)
        _curve.radius = self.curve.radius
        _curve.direction = self.curve.direction

        return arc.get_parameters(_curve, False)

    def _generate_internal_arc(self, attr, point, on_drag=False):
        """
        Generate the arc based on changes to the arc points / position
        """

        _pos = DragState().coordinates

        if not _pos:
            _pos = MouseState().coordinates
        else:
            _pos = Vector(_pos)

        _mouse_vec = \
            self.project_to_line(self.curve.pi, self.curve.get(point), _pos)

        _delta = _mouse_vec.Length - self.curve.get(attr)

        _attr_val = _delta + self.curve.get(attr)

        _curve = arc.Arc()

        _curve.bearing_in = self.curve.bearing_in
        _curve.bearing_out = self.curve.bearing_out
        _curve.pi = self.curve.pi
        _curve.delta = self.curve.delta
        _curve.direction = self.curve.direction
        _curve.set(attr, _attr_val)

        return arc.get_parameters(_curve, False)

    def validate(self, lt_tan=0.0, rt_tan=0.0):
        """
        Validate the arc's tangents against it's PI's
        points - the corodinates of the three PI nodes
        lt_tan, rt_tan - the length of the tangents of adjoining curves
        """

        if not self.drag_curve:
            self.drag_curve = self.curve

        _t = self.drag_curve.tangent
        _style = CoinStyles.DEFAULT

        _nodes = []

        for _v in self.pi_nodes:

            if _v.drag_point:
                _nodes.append(Vector(_v.drag_point))

            else:
                _nodes.append(Vector(_v.point))

        #test of left-side tangent validity
        _lt = _nodes[0].sub(_nodes[1]).Length

        self.is_valid = _t + lt_tan <= _lt

        #test for right-side tangent validity
        if self.is_valid:
            _rt = _nodes[1].sub(_nodes[2]).Length

            self.is_valid = _t + rt_tan <= _rt

        #update styles accordingly
        if not self.is_valid:
            _style = CoinStyles.ERROR

        super().set_style(_style, self.drag_style, self.drag_color)

    def finalize(self):
        """
        Cleanup the tracker
        """

        pass
