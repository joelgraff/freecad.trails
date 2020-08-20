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

from freecad.trails import ContextTracker, PolyLineTracker, LineTracker, Drag
from .curve_tracker import CurveTracker

from freecad_python_support.tuple_math import TupleMath

from ...geometry import arc
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
        self.last_rebuild = None

        #build a list of coordinates from curves in the geometry
        _nodes = [tuple(self.datum)]
        _nodes += [tuple(_v.get('PI'))\
            for _v in self.model.get('geometry') if _v.get('Type') != 'Line']

        _nodes += [tuple(self.model.get('meta').get('End'))]

        self.alignment_tracker = PolyLineTracker('alignment', _nodes, self.base)

        _i = 0

        for _l in self.alignment_tracker.lines:

            for _m in _l.markers:

                _m.name = 'PI_' + str(_i)
                _i += 1

        _curves = [Arc(_v) for _v in self.alignment.get_curves()]

        for _i, _curve in enumerate(_curves):
            self.curve_trackers.append(
                CurveTracker('curve_' + str(_i), _curve, self.base))

        _lines = self.alignment_tracker.lines
        _max = len(_lines) - 1

        #iterate the curves, then the alignment lines, adding the
        #starting marker on each line to the full drag callbacks
        for _i, _c in enumerate(self.curve_trackers):

            _p = None
            _n = None

            if _i > 0:
                _p = self.curve_trackers[_i - 1]

            if _i < _max - 1:
                _n = self.curve_trackers[_i + 1]

            for _j in range(_i, min(_i+3, _max)):

                for _m in _lines[_j].markers:
                    print('APPEND TO MARKER', _j)

                    for _v in [_p, _c, _n]:

                        if _v:
                            _m.before_drag_callbacks.append(_v.before_drag)

                    _m.on_drag_callbacks.append(self.on_drag_tracker)
                    _m.after_drag_callbacks.append(self.after_drag_tracker)

        #add the end marker on the last line
        _lines[-1].markers[-1].on_drag_callbacks.append(self.on_drag_tracker)

        _lines[-1].markers[-1].after_drag_callbacks.append(
            self.after_drag_tracker)

        self.set_visibility()

    def notify(self, event_type, message):
        """
        Override subscriber base implementation
        """

        #during dragging operations, sink all notifications here.
        #at the end of drag ops, pass on update to panel
        #if multiple nodes were selected, compute transformation
        #and pass on to panel

        super().notify(event_type, message, False)

        if event_type & Events.CURVE.UPDATED == event_type:

            if not self.drag_curves:

                _idx = int(message[0].split('-')[1])
                _first = max(0, _idx - 1)
                _last = min(len(self.trackers['Curves']), _idx + 2)

                for _v in self.trackers['Curves'][_first:_last]:
                    self.drag_curves.append(_v)

            self.validate_curves(self.drag_curves)

            self.dispatch(Events.ALIGNMENT.UPDATED, message, False)

        if event_type == Events.ALIGNMENT.UPDATE:
            self.dispatch(Events.NODE.UPDATE, message, False)

    def on_drag_tracker(self, user_data):
        """
        Adhoc callback to force update the curve drag tracker geometry
        by recaluclating it afresh
        """

        _names = ['PI', 'start', 'center', 'end']
        _has_name = [_v in user_data.obj.name for _v in _names]
        _pi_nums = [int(s) for s in user_data.obj.name if s.isdigit()]
        _matrix = Drag.drag_tracker.get_matrix()

        #pi change requires bearing update
        if _has_name[0]:
            self.rebuild_bearings(_matrix, _pi_nums)

    def after_drag_tracker(self, user_data):
        """
        Adhoc callback to force update the curve tracker geometry at
        the conclusion of a drag operation.
        """

        self.drag_copy = None

        for _c in self.curve_trackers:
            _c.drag_copy = None
            _c.update()

    def rebuild_bearings(self, matrix, pi_nums):
        """
        Recaluclate bearings and update curves accordingly
        """

        _xlate = matrix.getValue()[3]

        if _xlate == self.last_rebuild:
            return _result

        if  not pi_nums:
            return _result

        _pi_num = pi_nums[0]

        _bearing = SimpleNamespace(inbound=None, outbound=None)
        _pi = SimpleNamespace(prev=None, cur=None, next=None)
        _tan = SimpleNamespace(prev=None, next=None)

        _pi.cur = TupleMath.add(self.alignment_tracker.points[_pi_num], _xlate)

        _pi_range = list(range(_pi_num - 2, _pi_num + 3))

        _pi_points = [self.alignment_tracker.points[_v]\
            if 0 <= _v < len(self.alignment_tracker.points) else None\
                for _v in _pi_range]

        _pi_points[2] = _pi.cur

        _tan_len = []
        _pprev = None

        for _p in _pi_points:

            if not _p:
                _tan_len.append(None)
                continue

            if _pprev:
                _tan_len.append(
                    TupleMath.length(TupleMath.subtract(_p, _pprev)))

            _pprev = _p

        if _pi_points[1] is not None:
            _pi.prev = self.alignment_tracker.points[_pi_range[1]]

        if _pi_points[3] is not None:
            _pi.next = self.alignment_tracker.points[_pi_range[3]]

        if _pi.next:
            _tan.next = TupleMath.subtract(_pi.next, _pi.cur)
            _bearing.next = TupleMath.bearing(_tan.next)

        if _pi.prev:
            _tan.prev = TupleMath.subtract(_pi.cur, _pi.prev)
            _bearing.prev = TupleMath.bearing(_tan.prev)

        #iterate the curves to be changed by the change in PI and update their bearings

        _i = 0

        for _c in self.curve_trackers[
            max(0, _pi_num-2):min(_pi_num + 1, len(self.curve_trackers))]:

            #previous curve
            if not _i:
                _c.set_bearings(bearing_out = _bearing.prev)

            #next curve
            elif _i == 2:
                _c.set_bearings(bearing_in = _bearing.next)

            #curve under selected PI
            else:
                _c.set_pi(_pi.cur)
                _c.set_bearings(_bearing.prev, _bearing.next)

            _i += 1

            _c.update()

    def get_updates(self):
        """
        Return latest geometry updates in message queue
        """

        _queue_len = len(self.message_queue)

        if not _queue_len:
            return {}

        _result = []

        for _v in self.message_queue.values():
            _result.append(
                {
                    'position': _v['position'],
                    'translation': _v['translation'].getValue(),
                    'rotation': _v['rotation'].getValue()
                }
            )

        return _result

    def _update_status_bar(self):
        """
        Update the status bar with the latest mouseover data
        """

        self.status_bar.showMessage(
            MouseState().component + ' ' + str(tuple(MouseState().coordinates))
        )

    def on_drag(self):
        """
        Override base function
        """

        #iterate curves to find curves being dragged
        #if not self.drag_curves:

        #    self.drag_curves = [
        #        _v for _v in self.trackers['Curves'] if _v.state.dragging
        #    ]

    def validate_curves(self, curves):
        """
        Valuidate the list of curves against each other and their PI's
        """

        _last_tan = 0.0
        _max = len(curves) - 1

        for _i, _v in enumerate(curves):

            _next_tan = 0.0

            if _i < _max:

                _dc = curves[_i + 1]

                if _dc.drag_curve:
                    _next_tan = _dc.drag_curve.get('Tangent')

            _v.validate(_last_tan, _next_tan)
            _last_tan = _v.drag_curve.get('Tangent')

    def end_drag(self):
        """
        Override base fucntion
        """

        super().end_drag()

        self.drag_curves = []

    def post_select_event(self, arg):
        """
        Event to force wires to re-test selection state on button down
        """

        if MouseState().button1.state == 'UP':
            return

        for _v in self.trackers['Tangents']:
            _v.validate_selection()

    def button_event(self, arg):
        """
        Override base button actions
        """

        # dispatch an empty message if nothing is selected
        # abort if not multi-selecting or button up
        if MouseState().button1.state == 'UP':

            _sel = [_v.is_selected() for _v in self.trackers['Curves']]

            if not any(_sel):
                self.notify(Events.ALIGNMENT.EVENTS, [None, None])

            super().button_event(arg)
            return

        _pick = MouseState().component

        for _v in self.trackers['Nodes']:

            if not _v.is_visible():
                _v.set_visibility(True)

        #node selection is multi-select only
        if 'NODE' in _pick and MouseState().ctrlDown:

            #get the nodes we need to select, and select them
            _idx = int(_pick.split('-')[1]) + 1

            for _v in self.trackers['Nodes'][_idx:]:
                SelectState().select(_v, force=True)

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

    def _signalize_trackers(self):
        """
        Regsiter trackers appropriately as subscribers to one another
        """

        #subscribe node trackers to alignment and vice-versa
        for _v in self.trackers['Nodes']:
            self.register(_v, Events.NODE.UPDATE)

        #subscribe curves
        for _v in self.trackers['Curves']:

            _v.register(self, [Events.CURVE.UPDATED, Events.CURVE.SELECTED])
            self.register(_v, Events.CURVE.UPDATE)

    def _build_node_trackers(self, nodes, names):
        """
        Generate the node trackers for the alignment
        """

        _result = []

        #node trackers
        for _i, _pt in enumerate(nodes):

            _tr = NodeTracker(names=names + ['NODE-' + str(_i)], point=_pt)
            _result.append(_tr)

        _result[0].is_end_node = True
        _result[-1].is_end_node = True

        return _result

    def _build_wire_trackers(self, names):
        """
        Generate the tangent trackers for the alignment
        """

        _result = []

        #wire trackers - Tangents
        for _i in range(0, len(self.trackers['Nodes']) - 1):

            _nodes = self.trackers['Nodes'][_i:_i + 2]

            _wt = WireTracker(names=names + ['WIRE-' + str(_i)])

            _wt.set_selectability(False)
            _wt.set_points(nodes=_nodes)
            _wt.update()

            _result.append(_wt)

        return _result

    def _build_curve_trackers(self, names):
        """
        Generate the curve trackers for the alignment
        """

        _curves = [Arc(_v) for _v in self.alignment.get_curves()]
        _result = []

        for _i in range(0, len(self.trackers['Tangents']) - 1):

            print(type(_curves[_i]))
            _ct = CurveTracker(
                name='test' + str(_i),
                curve=_curves[_i],
                pi_list=self.trackers['Nodes'][_i:_i+3],
                parent=self.node,
                view = Gui.ActiveDocument.ActiveView
            )

            _result.append(_ct)

        return _result

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
