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
Tracker for alignment editing
"""

from FreeCAD import Vector
import FreeCADGui as Gui

from types import SimpleNamespace

from freecad.trails.design import ContextTracker, PolyLineTracker, Drag
from .curve_tracker import CurveTracker

from freecad_python_support.tuple_math import TupleMath

from ...geometry.arc import Arc

class AlignmentTracker(ContextTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, object_name, alignment, datum=Vector()):
        """
        Constructor
        """

        super().__init__(name='ALIGNMENT_TRACKER',
            view=Gui.ActiveDocument.ActiveView, parent=None)

        self.alignment = alignment
        self.status_bar = Gui.getMainWindow().statusBar()
        self.pi_list = []
        self.curve_trackers = []
        self.model = self.alignment.model.data
        self.datum = self.model.get('meta').get('Start')
        self.last_update = None
        self.pi_nodes = []
        self.drag_points = None
        self.curve_group = self.base.add_group('Curve_Group')
        self.alignment_group = self.base.add_group('Alignment_Group')

        #build a list of coordinates from curves in the geometry
        _nodes = [tuple(self.datum)]
        _nodes += [tuple(_v.get('PI'))\
            for _v in self.model.get('geometry') if _v.get('Type') != 'Line']

        _nodes += [tuple(self.model.get('meta').get('End'))]

        self.alignment_tracker =\
            PolyLineTracker('alignment', _nodes, self.alignment_group)

        _i = 0

        #build list of PI nodes from marker trackers
        for _l in self.alignment_tracker.lines:

            _j = 0

            for _m in _l.markers:

                _m.name = 'PI_' + str(_i)
                _i += 1

                if not _j:
                    self.pi_nodes.append(_m)
                    _j = +1

        self.pi_nodes.append(self.alignment_tracker.lines[-1].markers[-1])

        _curves = [Arc(_v) for _v in self.alignment.get_curves()]

        for _i, _curve in enumerate(_curves):
            self.curve_trackers.append(
                CurveTracker(str(_i), _curve, self.curve_group))

        _lines = self.alignment_tracker.lines

        #Add dragging callbacks to the markers and lines
        #on_drag callbacks omitted as the alignment tracker needs to run first
        #and call curve updates driectly.
        for _i, _c in enumerate(self.curve_trackers):

            #before/after drag for markers
            for _j in range(_i,_i+3):
                self.pi_nodes[_j].before_drag_callbacks.append(_c.before_drag)
                self.pi_nodes[_j].after_drag_callbacks.append(_c.after_drag)

            #before/after drag for lines
            for _j in range(max(0, _i - 1), min((_i + 3), len(_lines))):
                _lines[_j].before_drag_callbacks.append(_c.before_drag)
                _lines[_j].after_drag_callbacks.append(_c.after_drag)

            #append curve validation during drag ops against alignment tangents
            _c.on_drag_callbacks.append(self.validate_curve_drag)

        #line and node on_drag/after_drag callbacks
        for _l in _lines:

            _l.before_drag_callbacks.append(self.before_drag_tracker)
            _l.on_drag_callbacks.append(self.on_drag_tracker)
            _l.after_drag_callbacks.append(self.after_drag_tracker)

        for _m in self.pi_nodes:

            _m.before_drag_callbacks.append(self.before_drag_tracker)
            _m.on_drag_callbacks.append(self.on_drag_tracker)
            _m.after_drag_callbacks.append(self.after_drag_tracker)

        self.set_visibility()

        self.drag_points = self.alignment_tracker.points

    def validate_curve_drag(self, user_data):
        """
        Validates the changes to the curves, noting errors when
        curves overlap or exceed tangent lengths
        """

        _prev_curve = None
        _curve = None
        _max = len(self.curve_trackers)

        _pp = self.drag_points[0]
        _lines = []

        for _p in self.drag_points[1:]:
            _lines.append(TupleMath.length(_p, _pp))
            _pp = _p

        for _i, _l in enumerate(_lines):

            _is_invalid = False

            #the last segment doesn't need _prev_curve
            if _i < _max:
                _curve = self.curve_trackers[_i]

            else:

                #abort if last curve has already been marked invalid
                if _curve.is_invalid:
                    return

                _prev_curve = None

            #calculate sum of tangnets
            _tan = _curve.arc.tangent

            if _prev_curve:
                _tan += _prev_curve.arc.tangent

            #curve tangents must not exceed segment length
            _is_invalid = _tan > _l

            #invalidate accordingly.
            _curve.is_invalid = _is_invalid

            if _prev_curve and not _prev_curve.is_invalid:
                _prev_curve.is_invalid = _is_invalid

            _prev_curve = _curve


    def before_drag_tracker(self, user_data):
        """
        Callback to set alignment behaviors for the DragTracker
        """

        Drag.drag_tracker.set_constraint_geometry()

    def on_drag_tracker(self, user_data):
        """
        Adhoc callback to force update the curve drag tracker geometry
        by recaluclating it afresh
        """

        if not self.alignment_tracker.points:

            self.alignment_tracker.points = self.alignment_tracker.get_coordinates()

        _names = ['PI', 'segment']

        if not any(_v in user_data.obj.name for _v in _names):
            return

        _pi_nums = [int(''.join(filter(str.isdigit, user_data.obj.name)))]

        if 'segment' in user_data.obj.name:
            _pi_nums.append(_pi_nums[0] - 1)

        #pi change requires bearing update
        self.rebuild_bearings(user_data.matrix, _pi_nums)
        self.validate_curve_drag(None)

    def after_drag_tracker(self, user_data):
        """
        Adhoc callback to force update the curve tracker geometry at
        the conclusion of a drag operation.
        """

        self.drag_copy = None
        self.alignment_tracker.points = None

        for _l in self.alignment_tracker.lines:
            _l.update()

    def rebuild_bearings(self, matrix, pi_nums):
        """
        Recaluclate bearings and update curves accordingly
        """

        _xlate = matrix.getValue()[3]

        if _xlate == self.last_update:
            return

        if not pi_nums:
            return

        self.last_update=_xlate

        _pi = SimpleNamespace(
            start=0, end=0, points=self.alignment_tracker.points.copy(),
            bearings=[], count=len(self.alignment_tracker.points))

        _pi.start = min(pi_nums)
        _pi.end = max(pi_nums) + 1

        _p = self.view_state.transform_points(
            _pi.points[_pi.start:_pi.end], matrix)

        #apply translation to selected PI's
        #for _i in range(_pi.start, _pi.end):
        #    _pi.points[_i] = TupleMath.add(_pi.points[_i], _xlate)

        _pi.points[_pi.start:_pi.end] = _p

        #get range of PI's for bearing calcs
        _pi.start = max(_pi.start - 2, 0)
        _pi.end = min(_pi.end + 2, _pi.count)
        _pi.points = _pi.points[_pi.start:_pi.end]
        _pi.count = len(_pi.points)

        for _i, _p in enumerate(_pi.points):

            _b = SimpleNamespace(inb = None, outb = None)

            if _p is None:
                _pi.bearings.append(_b)
                continue

            #calc inbound / outbound bearings
            if _i < _pi.count - 1:

                _b.outb = TupleMath.bearing(
                    TupleMath.subtract(_pi.points[_i + 1], _p))

            if _i > 0:

                _b.inb = TupleMath.bearing(
                    TupleMath.subtract(_p, _pi.points[_i - 1]))

            _pi.bearings.append(_b)

        _curve = SimpleNamespace(
            start=max(_pi.start, 0), end=_pi.end - 1)

        for _i, _c in enumerate(self.curve_trackers[_curve.start:_curve.end]):

            _b = _pi.bearings[_i + 1]
            _c.set_pi(_pi.points[_i + 1])
            _c.set_bearings(_b.inb, _b.outb)

            _c.update()

        self.drag_points = _pi.points

    #------------
    # LEGACY
    #------------

    def _update_status_bar(self):
        """
        Update the status bar with the latest mouseover data
        """

        self.status_bar.showMessage(
            MouseState().component + ' ' + str(tuple(MouseState().coordinates))
        )

    def build_trackers(self):
        """
        Build the node and wire trackers that represent the selectable
        portions of the alignment geometry
        """

        _names = self.names[:2]
        _model = self.alignment.model.data

        #build a list of coordinates from curves in the geometry
        _nodes = [Vector()]
        _nodes += [_v.get('PI')\
            for _v in _model.get('geometry') if _v.get('Type') != 'Line']

        _nodes += [_model.get('meta').get('End')]


        #build the trackers
        self.trackers['Nodes'] = self._build_node_trackers(_nodes, _names)
        self.trackers['Tangents'] = self._build_wire_trackers(_names)
        self.trackers['Curves'] = self._build_curve_trackers(_names)

        #self._signalize_trackers()

    def finalize(self):
        """
        Cleanup the tracker
        """

        for _t in self.curve_trackers:
            _t.finalize()

        self.remove_node(self.groups['EDIT'], self.get_node())
        self.remove_node(self.groups['DRAG'], self.get_node())

        if self.callbacks:
            for _k, _v in self.callbacks.items():
                ViewState().view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        super().finalize()
