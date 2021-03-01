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

import math
from itertools import chain

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

        self.drag_refs = SimpleNamespace(
            pi_list = (),       #list of PI's for bearing calcs
            curve_list = (),    #list of curves to update
            selected_pi = (),   #list of pi's actually selected
            start_points = None,#list of PI points in their initial state
            drag_points = None, #list of PI points as they're dragged
            last_update = None  #last translation update
        )

        self.curve_trackers = []
        self.model = self.alignment.model.data
        self.datum = self.model.get('meta').get('Start')

        self.pi_nodes = []

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
        for _k, _l in enumerate(self.alignment_tracker.lines):

            _j = 0
            _l.type_name += f'.Alignment.Tangent.{str(_k).zfill(3)}'

            for _m in _l.markers:

                _m.name = f'PI_{str(_i).zfill(3)}'
                _m.type_name += f'.Alignment.PI.{str(_i).zfill(3)}'
                _i += 1

                if not _j:
                    self.pi_nodes.append(_m)
                    _j = +1

        self.pi_nodes.append(self.alignment_tracker.lines[-1].markers[-1])

        _curves = [Arc(_v) for _v in self.alignment.get_curves()]

        for _i, _curve in enumerate(_curves):

            _ct = CurveTracker(
                f'CurveTracker_{str(_i)}', _curve, self.curve_group)

            _ct.type_name += f'.{str(_i).zfill(3)}'

            self.curve_trackers.append(_ct)

        _lines = self.alignment_tracker.lines

        #Add dragging callbacks to the markers and lines
        for _i, _c in enumerate(self.curve_trackers):

            #before/after drag for markers
            for _n in self.pi_nodes[_i:_i+3]:

                _n.before_drag_callbacks.append(_c.before_drag)
                #_n.on_drag_callbacks.append(_c.on_drag)
                _n.after_drag_callbacks.append(_c.after_drag)

            for _l in _lines[max(_i-2,0):min(_i+3, len(_lines)+1)]:

                _l.before_drag_callbacks.append(_c.before_drag)
                #_n.on_drag_callbacks.append(_c.on_drag)
                _l.after_drag_callbacks.append(_c.after_drag)

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

    def validate_curve_drag(self, user_data):
        """
        Validates the changes to the curves, noting errors when
        curves overlap or exceed tangent lengths
        """

        _prev_curve = None
        _curve = None
        _max = len(self.curve_trackers)

        _pp = self.drag_refs.drag_points[0]
        _lines = []

        #get the distance between each PI for tangent length comparisons
        for _p in self.drag_refs.drag_points[1:]:
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

        self.drag_refs.start_points = self.alignment_tracker.get_coordinates()

        Drag.drag_tracker.set_constraint_geometry()

        _num = int(''.join(
            [_v for _v in user_data.obj.name if str.isdigit(_v)]))

        _count = len(self.drag_refs.start_points)

        _sel_pi = (_num,)

        if 'segment' in user_data.obj.name:
            _sel_pi += (_num + 1,)

        #boolean flags for selected PIs
        self.drag_refs.selected_pi = [_v in _sel_pi for _v in range(0, _count)]

        _curve_list = [set(range(_v-2, _v+1)) for _v in _sel_pi]
        _pi_list = [set(range(_v-2, _v+3)) for _v in _sel_pi]

        if len(_sel_pi) > 1:
            _curve_list = set.union(*_curve_list)
            _pi_list = set.union(*_pi_list)

        else:
            _curve_list = _curve_list[0]
            _pi_list = _pi_list[0]

        #constrain the lists to valid ranges
        self.drag_refs.curve_list =\
            tuple(_curve_list.intersection(set(range(0, _count-2))))

        self.drag_refs.pi_list =\
            tuple(_pi_list.intersection(set(range(0, _count))))

        _pi = (tuple(_pi_list)[0], tuple(_pi_list)[-1] + 1)

        self.drag_refs.start_points =\
            self.drag_refs.start_points[_pi[0]:_pi[1]]

        self.drag_refs.selected_pi =\
            self.drag_refs.selected_pi[_pi[0]:_pi[1]]

    def on_drag_tracker(self, user_data):
        """
        Update the CurveTracker geometry when tangents are adjusted
        """

        #pi change requires bearing update
        self.rebuild_bearings(user_data.matrix, user_data.obj.name)

        self.validate_curve_drag(None)

    def after_drag_tracker(self, user_data):
        """
        Adhoc callback to force update the curve tracker geometry at
        the conclusion of a drag operation.
        """

        self.drag_copy = None
        self.start_points = None

        self.drag_refs = SimpleNamespace(
            pi_list = (),
            curve_list = (),
            selected_pi = (),
            start_points = None,
            drag_points = None,
            last_update = None
        )

        for _l in self.alignment_tracker.lines:
            _l.update()

    def rebuild_bearings(self, matrix, obj_name):
        """
        Recalculate bearings / update curves
        """

        #capture point translation
        _xlate = matrix.getValue()[3]

        #abort if no movement has occurred
        if _xlate == self.drag_refs.last_update:
            return

        self.drag_refs.last_update = _xlate

        #get the points and transform the selected points by current translation
        _p = [_v for _i, _v in enumerate(self.drag_refs.start_points)\
            if self.drag_refs.selected_pi[_i]]

        _p = self.view_state.transform_points(_p, matrix)

        _points = []
        _j = 0

        #update translated points
        for _i, _v in enumerate(self.drag_refs.start_points):

            if self.drag_refs.selected_pi[_i]:

                _points.append(_p[_j])
                _j += 1

            else:
                _points.append(_v)

        #precalcualte bearings
        _bearings = [TupleMath.bearing(
            TupleMath.subtract(_points[_i+1], _points[_i]))\
                for _i, v in enumerate(_points[:-1])]

        #iterate curves setting the bearing inbound / outbound pairs
        for _i, _c in enumerate(self.curve_trackers[
            self.drag_refs.curve_list[0]:self.drag_refs.curve_list[-1] + 1]):

            _c.set_pi(_points[_i + 1])
            _c.set_bearings(_bearings[_i], _bearings[_i + 1])

            _c.update()

        self.drag_refs.drag_points = _points

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
