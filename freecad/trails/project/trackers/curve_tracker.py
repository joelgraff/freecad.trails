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

from FreeCAD import Vector
from pivy import coin

from ...geometry import support, arc, spiral

from ..support.mouse_state import MouseState
from ..support.drag_state import DragState

from .wire_tracker import WireTracker
from .coin_styles import CoinStyles

class CurveTracker(WireTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, names, curve, pi_nodes):
        """
        Constructor
        """

        super().__init__(names=names)

        self.curve = curve
        self.pi_nodes = pi_nodes
        self.is_valid = True
        self.drag_arc = None
        self.drag_style = None
        self.drag_start_dist = 0.0

        if isinstance(self.curve, dict):
            self.curve = arc.Arc(self.curve)

        self.update_curve()

    def button_event(self, arg):
        """
        Override base button event
        """

        #do nothing as curve selection is handled in alignment tracker
        pass

    def start_drag(self):
        """
        Override base implementation
        """

        super().start_drag()

        self.drag_start_dist = DragState().start.sub(self.curve.pi).Length

    def on_drag(self):
        """
        Override base implementation
        """

        _curve = self._generate_arc(lock_attr='Tangent')
        _points = arc.get_points(_curve, _dtype=tuple)

        _node = self.drag_group.getChild(0).getChild(3).point
        _node.setValues(0, len(_points), _points)

    def update_curve(self, curve=None):
        """
        Update the curve based on the passed data points
        """

        if not self.is_valid:
            return

        if curve is None:
            curve = self.curve

        else:
            self.curve = curve

        _points = None

        #print('\n\tcurve = \n', curve)
        if curve.type == 'Spiral':
            _points = self._generate_spiral()

        else:
            _points = arc.get_points(self.curve)

        if not _points:
            return

        super().update(_points)

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

    def _generate_arc(self, lock_attr='Radius', on_drag=False):
        """
        Generate a simple arc curve
        """

        _pos = MouseState().coordinates
        _scale = MouseState().coordinates.sub(self.curve.pi).Length\
            / self.drag_start_dist

        _vec = self.curve.center.sub(self.curve.pi).normalize()

        if MouseState().shiftDown:
            _scale *= 0.10

        DragState().node_translate.translation.setValue(
            tuple(_vec.multiply(_scale))
        )

        _ctr = self.curve.pi.add(_vec.multiply(self.curve.middle))

        _curve = arc.Arc()
        _curve.bearing_in = self.curve.bearing_in
        _curve.bearing_out = self.curve.bearing_out
        _curve.pi = self.curve.pi
        _curve.center = _ctr

        return arc.get_parameters(_curve, False)

    def validate(self, lt_tan=0.0, rt_tan=0.0):
        """
        Validate the arc's tangents against it's PI's
        points - the corodinates of the three PI nodes
        lt_tan, rt_tan - the length of the tangents of adjoining curves
        """

        if not self.drag_arc:
            return

        if not self.state.dragging:
            return

        if not self.drag_style:
            return

        _t = self.drag_arc.tangent
        _style = CoinStyles.DEFAULT

        _nodes = []

        for _v in self.pi_nodes:

            if _v.drag_point:
                _nodes.append(Vector(_v.drag_point))

            else:
                _nodes.append(Vector(_v.point))

        #test of left-side tangent validity
        _lt = _nodes[0].sub(_nodes[1]).Length

        print('\n\t', self.name)
        print('left ->', _t, lt_tan, _t + lt_tan, _lt)
        self.is_valid = _t + lt_tan <= _lt

        #test for right-side tangent validity
        if self.is_valid:
            _rt = _nodes[1].sub(_nodes[2]).Length
            print('right ->', _t, rt_tan, _t + rt_tan, _rt)

            self.is_valid = _t + rt_tan <= _rt

        #update styles accordingly
        if not self.is_valid:
            _style = CoinStyles.ERROR

        super().set_style(_style, self.drag_style, self.drag_color)

    def finalize(self):
        """
        Cleanup the tracker
        """

        super().finalize()
