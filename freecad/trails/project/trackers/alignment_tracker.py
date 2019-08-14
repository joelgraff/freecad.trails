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

from pivy import coin

from FreeCAD import Vector

import FreeCADGui as Gui

from .base_tracker import BaseTracker

from ..support.mouse_state import MouseState
from ..support.view_state import ViewState

from ..support.drag_state import DragState

from .node_tracker import NodeTracker
from .wire_tracker import WireTracker
from .curve_tracker import CurveTracker

class AlignmentTracker(BaseTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, doc, object_name, alignment, datum=Vector()):
        """
        Constructor
        """

        self.alignment = alignment
        self.doc = doc
        self.names = [doc.Name, object_name, 'ALIGNMENT_TRACKER']
        self.user_dragging = False
        self.status_bar = Gui.getMainWindow().statusBar()
        self.pi_list = []
        self.datum = alignment.model.data.get('meta').get('Start')

        self.drag = DragState()

        #base (placement) transformation for the alignment
        self.transform = coin.SoTransform()
        self.transform.translation.setValue(
            tuple(alignment.model.data.get('meta').get('Start'))
        )
        super().__init__(names=self.names, children=[self.transform])

        #scenegraph node structure for editing and dragging operations
        self.groups = {
            'EDIT': coin.SoGroup(),
            'DRAG': coin.SoGroup(),
            'SELECTED': coin.SoSeparator(),
            'PARTIAL': coin.SoSeparator(),
        }

        self.drag_transform = coin.SoTransform()

        #add two nodes to the drag group - the transform and a dummy node
        #which provides a way to access the transform matrix
        self.groups['SELECTED'].addChild(self.drag_transform)
        self.groups['SELECTED'].addChild(coin.SoSeparator())

        self.groups['DRAG'].addChild(self.groups['SELECTED'])
        self.groups['DRAG'].addChild(self.groups['PARTIAL'])

        self.node.addChild(self.groups['EDIT'])
        self.node.addChild(self.groups['DRAG'])

        #generate initial node trackers and wire trackers for mouse interaction
        #and add them to the scenegraph
        self.trackers = None
        self.build_trackers()

        _trackers = []
        for _v in self.trackers.values():
            _trackers.extend(_v)

        for _v in _trackers:
            self.insert_node(_v.switch, self.groups['EDIT'])

        #insert in the scenegraph root
        self.insert_node(self.switch)

    def _update_status_bar(self):
        """
        Update the status bar with the latest mouseover data
        """

        self.status_bar.showMessage(
            MouseState().component + ' ' + str(tuple(MouseState().coordinates))
        )

    def button_event(self, arg):
        """
        Override base button actions
        """

        #multi-select
        _pick = MouseState().component

        if not _pick:
            return

        if MouseState().button1.state == 'UP':
            return

        #if a curve is picked, set the visibility ignore flag on, so the
        #curve PI doesn't get redrawn
        #if 'CURVE' in _pick:

        #    _idx = int(_pick.split('-')[1])

        #    self.trackers['Nodes'][_idx + 1].state.visible.ignore = True

        if 'NODE' in _pick:

            _idx = int(_pick.split('-')[1])

            _nodes = [self.trackers['Nodes'][_idx]]

            if MouseState().ctrlDown:
                _nodes = self.trackers['Nodes'][_idx:]

            for _v in _nodes:
                _v.state.selected.value = True
                _v.state.selected.ignore_once()

    def build_trackers(self):
        """
        Build the node and wire trackers that represent the selectable
        portions of the alignment geometry
        """

        _model = self.alignment.model.data

        #build a list of coordinates from curves in the geometry
        _nodes = [Vector()]

        for _geo in _model.get('geometry'):

            if _geo.get('Type') != 'Line':
                _nodes += [_geo.get('PI')]

        _nodes += [_model.get('meta').get('End')]

        #build the trackers
        _names = self.names[:2]
        _result = {'Nodes': [], 'Tangents': [], 'Curves': []}

        #node trackers
        for _i, _pt in enumerate(_nodes):

            _tr = NodeTracker(
                names=_names[:2] + ['NODE-' + str(_i)], point=_pt
            )
            _result['Nodes'].append(_tr)

        _result['Nodes'][0].is_end_node = True
        _result['Nodes'][-1].is_end_node = True

        #wire trackers - Tangents
        for _i in range(0, len(_result['Nodes']) - 1):

            _nodes = _result['Nodes'][_i:_i + 2]

            _result['Tangents'].append(
                self._build_wire_tracker(
                    wire_name=_names[:2] + ['WIRE-' + str(_i)],
                    nodes=_nodes,
                    points=[], #[_v.point for _v in _nodes],
                    select=False
                )
            )

        _curves = self.alignment.get_curves()
        _names = self.names[:2]

        #curve trackers
        for _i in range(0, len(_result['Tangents']) - 1):

            _ct = CurveTracker(
                names=_names[:2] + ['CURVE-' + str(_i)],
                curve=_curves[_i],
                pi_nodes=_result['Nodes'][_i:_i+3]
            )

            _ct.set_selectability(True)

            _result['Nodes'][_i + 1].conditions.append(_ct.name)
            _result['Curves'].append(_ct)

        self.trackers = _result

    def _build_wire_tracker(self, wire_name, nodes, points, select=False):
        """
        Convenience function for WireTracker construction
        """

        _wt = WireTracker(names=wire_name)

        _wt.set_selectability(select)
        _wt.set_points(points, nodes)
        _wt.update()

        return _wt

    def _dep_validate_alignment(self):
        """
        Given a list of updated curves, validate them against themselves
        and adjoining geometry
        """

        curves = [_v.curve for _v in self.trackers['Curves']]

        #append preceding and following curves if first / last curves
        #aren't being updated
        if _idx[0] > 0:
            _idx.insert(0, _idx[0] - 1)
            curves.insert(0, self.curves[_idx[0]])

        elif _idx[-1] < len(self.curves) - 1:
            _idx.append(_idx[-1] + 1)
            curves.append(self.curves[_idx[-1]])

        _styles = [CoinStyles.DEFAULT]*len(curves)

        #validate curves against each other,
        #ensuring PI distance >= sum  of curve tangents
        for _i in range(0, len(curves) - 1):

            _tangents = []
            _pair = [curves[_i], curves[_i + 1]]

            for _c in _pair:

                if _c.get('Type') == 'Spiral':

                    _tangents.append(spiral.get_ordered_tangents(_c)[0])
                    continue

                _tangents.append(_c['Tangent'])

            if (_tangents[0] + _tangents[1])\
                > (_pair[0].get('PI').distanceToPoint(_pair[1].get('PI'))):

                _styles[_i + 1] = CoinStyles.ERROR
                _styles[_i] = CoinStyles.ERROR

        #do endpoint checks if the first or last curves are changing.
        _x = []

        #first curve is updating
        if _idx[0] == 0:
            _x.append(0)

        #last curve is updating
        if _idx[-1] == len(self.curves) - 1:
            _x.append(-1)

        for _i in _x:

            _c = curves[_i]
            _p = self.trackers['Nodes'][_i].get()
            _tangent = None

            #disable validation for spirals temporarily
            if _c.get('Type') == 'Spiral':

                _tans = spiral.get_ordered_tangents(_c)
                _tangent = _tans[1]

                if _i == 0:
                    _tangent = _tans[0]

            else:
                _tangent = _c['Tangent']

            if _styles[_i] != CoinStyles.ERROR \
                and _tangent > _c.get('PI').distanceToPoint(_p):

                _styles[_i] = CoinStyles.ERROR

        for _i, _v in enumerate(_styles):

            _t = self.trackers['Curves'][_idx[0] + _i]

            _t.set_base_style(_v)
            _t.set_style(_v)

        self.drag.is_valid = all([_v != CoinStyles.ERROR for _v in _styles])

    def finalize(self):
        """
        Cleanup the tracker
        """

        for _t in self.trackers.values():

            for _u in _t:
                _u.finalize()

        self.remove_node(self.groups['EDIT'], self.node)
        self.remove_node(self.groups['DRAG'], self.node)

        if self.callbacks:
            for _k, _v in self.callbacks.items():
                ViewState().view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        super().finalize()
