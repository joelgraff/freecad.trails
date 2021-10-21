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
from pivy_trackers.coin.coin_utils import *
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
            selected = SimpleNamespace(
                pi = None,   #list of pi's actually selected
                indices = None), #list of PI indices

            points = None, #list of PI points
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

            _c.after_drag_callbacks.append(self.after_drag_tracker)

            #before/after drag for markers
            for _n in self.pi_nodes[_i:_i+3]:

                _n.before_drag_callbacks.append(_c.before_drag)
                _n.after_drag_callbacks.append(_c.after_drag)

            for _l in _lines[max(_i-2,0):min(_i+3, len(_lines)+1)]:

                _l.before_drag_callbacks.append(_c.before_drag)
                _l.after_drag_callbacks.append(_c.after_drag)

            _c.before_drag_callbacks.append(self.before_drag_tracker)
            _c.on_drag_callbacks.append(self.on_drag_tracker)

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

        Drag.drag_tracker.drag.full.set_translation((0.0, 0.0, 0.0))
        Drag.drag_tracker.drag.full.set_rotation(0.0, (0.0, 0.0, 0.0))

    def validate_curve_drag(self, user_data):
        """
        Validates the changes to the curves, noting errors when
        curves overlap or exceed tangent lengths
        """

        #drag_refs.curve_list = Curves immediately under selected points + primary and secondary immediate curves

        #drag_refs.pi_list = PI's of curves in curve_list

        #lengths =  distances between n curves

        #get distances between PI's except first and last

        _pp = self.drag_refs.points[0]
        _lines = []
        _curves = self.curve_trackers[
            self.drag_refs.curve_list[0]:self.drag_refs.curve_list[-1] +1]

        for _p in self.drag_refs.points[1:]:
            _lines.append(TupleMath.length(_p, _pp))
            _pp = _p

        _prev = _curves[0]
        _prev.is_invalid = False
        _any_viz_invalid = False

        for _i, _c in enumerate(_curves[1:]):

            _c.is_invalid = False

            _invalid = [
                _prev.is_invalid or _prev.arc.tangent > _lines[_i],
                (_prev.arc.tangent + _c.arc.tangent) > _lines[_i + 1]
            ]

            if not _any_viz_invalid:
                _any_vizinvalid = any(_invalid)

            _prev.is_invalid = any(_invalid)
            _c.is_invalid = _invalid[1]

            _prev = _c

        #test last curve tangent length against the end tangent
        _prev.is_invalid = _prev.is_invalid\
            or _prev.arc.tangent > _lines[-1]

        if _prev.is_invalid:
            _any_viz_invalid = True

        #if *any* curve was invalidated at any point, all curves need to be
        #invalidated for final update
        if _any_viz_invalid:
            for _c in _curves:
                _c.is_invalid = True

    def before_drag_tracker(self, user_data):
        """
        Callback to set alignment behaviors for the DragTracker
        """

        self.drag_refs.points = self.alignment_tracker.get_coordinates()

        Drag.drag_tracker.set_constraint_geometry()

        _num = int(''.join(
            [_v for _v in user_data.obj.name if str.isdigit(_v)]))

        _count = len(self.drag_refs.points)

        _sel_pi = (_num,)

        if 'segment' in user_data.obj.name:
            _sel_pi += (_num + 1,)

        elif 'Curve'  in user_data.obj.type_name:
            _sel_pi = (_num + 1,)

        #references to selected points
        self.drag_refs.selected.pi = [self.drag_refs.points[_v] \
                for _v in range(0, _count) if _v in _sel_pi]

        self.drag_refs.selected.indices = _sel_pi

        _curve_list = [set(range(_v-3, _v+2)) for _v in _sel_pi]
        _pi_list = [set(range(_v, _v+3)) for _v in _curve_list[0]]

        _curve_list = set.union(*_curve_list)
        _pi_list = set.union(*_pi_list)

        #constrain the lists to valid ranges
        self.drag_refs.curve_list =\
            tuple(_curve_list.intersection(set(range(0, _count-2))))

        self.drag_refs.pi_list =\
            tuple(sorted(_pi_list.intersection(set(range(0, _count)))))

        _pi = (tuple(
            self.drag_refs.pi_list)[0], tuple(self.drag_refs.pi_list)[-1]+1)

        self.drag_refs.points =\
            self.drag_refs.points[_pi[0]:_pi[1]]

        self.drag_refs.selected.indices =\
            [_v - _pi[0] for _v in self.drag_refs.selected.indices]

    def on_drag_tracker(self, user_data):
        """
        Update the CurveTracker geometry when tangents are adjusted
        """

        #if curves are being directly adjusted, don't recalculate bearings
        if not  'Curve' in user_data.obj.type_name:

            #pi change requires bearing update
            self.rebuild_bearings(user_data.matrix, user_data.obj.name)

        self.validate_curve_drag(None)

    def after_drag_tracker(self, user_data):
        """
        Adhoc callback to force update the curve tracker geometry at
        the conclusion of a drag operation.
        """

        #if the drag refs have been destroyed, abort - we've been here before
        if not self.drag_refs.points:
            return

        _curves = self.curve_trackers[
            self.drag_refs.curve_list[0]:self.drag_refs.curve_list[-1] + 1]

        #abort if any curves were invalidated during dragging
        if any([_c.is_invalid for _c in _curves]):

            for _c in _curves:
                _c.invalidate()

            self.alignment_tracker.invalidate()

        #destroy drag references for this dragging operation
        self.drag_refs = SimpleNamespace(
            pi_list = (),
            curve_list = (),
            selected = SimpleNamespace(
                pi = None,
                indices = None),
            points = None,
            last_update = None
        )

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

        _p = self.view_state.transform_points(
            self.drag_refs.selected.pi, matrix)

        _points = self.drag_refs.points
        _j = 0

        #update translated points
        for _i in self.drag_refs.selected.indices:

            _points[_i] = _p[_j]
            _j += 1

        #precalcualte bearings
        _bearings = [TupleMath.bearing(
            TupleMath.subtract(_points[_i+1], _v))\
                for _i, _v in enumerate(_points[:-1])]

        #iterate curves setting the bearing inbound / outbound pairs
        #drop the outermost curves as they are not being changed
        _curves = [self.curve_trackers[_c] for _c in self.drag_refs.curve_list]

        for _i, _c in enumerate(_curves):

            _c.set_pi(_points[_i + 1])
            _c.set_bearings(_bearings[_i], _bearings[_i + 1])
            _c.update()

        self.drag_refs.points = _points

    def finish(self):
        """
        Cleanup the tracker
        """

        for _t in self.curve_trackers:
            _t.finish()

        remove_child(self.curve_group, self.base.root)
        remove_child(self.alignment_group, self.base.root)

        if self.callbacks:
            for _k, _v in self.callbacks.items():
                ViewState().view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        super().finish()

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
