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

from pivy import coin

from FreeCAD import Vector

import FreeCADGui as Gui

from ...geometry import support, arc, spiral

from .base_tracker import BaseTracker
from .coin_style import CoinStyle

from ..support.utils import Constants as C
from ..support.mouse_state import MouseState

from ..containers import DragState

from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

class CurveTracker(BaseTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, view, names, curve, pi_nodes):
        """
        Constructor
        """

        self.curve = curve
        self.pi_nodes = pi_nodes
        self.callbacks = {}
        self.names = names
        self.mouse = MouseState()
        self.user_dragging = False
        self.is_valid = True
        self.status_bar = Gui.getMainWindow().statusBar()
        self.drag = DragState()
        self.view = view
        self.state = 'UNSELECTED'
        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        super().__init__(names=self.names)

        #input callback assignments
        self.callbacks = {
            'SoLocation2Event':
            self.view.addEventCallback('SoLocation2Event', self.mouse_event),

            'SoMouseButtonEvent':
            self.view.addEventCallback('SoMouseButtonEvent', self.button_event)
        }

        #scenegraph node structure for editing and dragging operations
        self.groups = {
            'EDIT': coin.SoGroup(),
            'DRAG': coin.SoGroup(),
        }

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
            self.insert_node(_v.node, self.groups['EDIT'])

        #insert in the scenegraph root
        self.insert_node(self.node)

    def _update_status_bar(self, info):
        """
        Update the status bar with the latest mouseover data
        """

        pass
        #_id = ''

        #if info:
        #    _id = info['Component']

        #_pos = self.view.getPoint(self.mouse.pos)

        #if 'NODE' in _id:
        #    _pos = self.datum.add(
        #        self.trackers['Nodes'][int(_id.split('-')[1])].get()
        #    )

        #_msg = _id + ' ' + str(tuple(_pos))

        ##self.status_bar.clearMessage()
        #self.status_bar.showMessage(_msg)

    def mouse_event(self, arg):
        """
        Manage mouse actions affecting multiple nodes / wires
        """

        _p = self.view.getCursorPos()

        self.mouse.update(arg, _p)

        self._update_status_bar(self.view.getObjectInfo(_p))

    def button_event(self, arg):
        """
        Manage button actions affecting multiple nodes / wires
        """

        self.mouse.update(arg, self.view.getCursorPos())

        self.state = 'UNSELECTED'

        if any([_v.state == 'SELECTED' for _v in self.pi_nodes]):
            self.state = 'SELECTED'

        #terminate dragging if button is released
        if self.user_dragging and not self.mouse.button1.dragging:
            self.end_drag()
            self.user_dragging = False

    def build_trackers(self):
        """
        Build the node and wire trackers that represent the selectable
        portions of the curve geometry
        """

        _node_names = ['Center', 'Start', 'End', 'PI', 'Center']
        _wires = (
            ('Start Radius', 1, 0),
            ('Start Tangent', 1, 3),
            ('End Radius', 2, 0),
            ('End Tangent', 2, 3)
        )

        #build a list of coordinates from curves in the geometry
        #skipping the last (duplicate of center)
        _coords = [self.curve[_k] for _k in _node_names[:-1]]

        #build the trackers
        _result = {'Nodes': [], 'Wires': [], 'Curve': None}

        #node trackers - don't create a PI node
        for _i, _pt in enumerate(_coords[:-1]):

            _names = self.names[:]
            _names[-1] = _names[-1] + '-' + _node_names[_i]

            _tr = NodeTracker(
                view=self.view,
                names=_names,
                point=_pt
            )

            _tr.update(_pt)

            _result['Nodes'].append(_tr)

        #wire trackers
        for _i, _v in enumerate(_wires):

            _result['Wires'].append(
                self._build_wire_tracker(
                    wire_name=self.names + [_v[0]],
                    nodes=_result['Nodes'],
                    points=[_coords[_v[1]], _coords[_v[2]]]
                )
            )

        _points = []

        #curve wire tracker
        _class = arc

        if self.curve['Type'] == 'Spiral':
            _class = spiral

        _points = _class.get_points(self.curve)

        _result['Curve'] = [
            self._build_wire_tracker(
                wire_name=self.names + [self.curve['Type']],
                nodes=_result['Nodes'],
                points=_points,
                select=True
            )
        ]

        self.trackers = _result

    def _build_wire_tracker(self, wire_name, nodes, points, select=False):
        """
        Convenience function for WireTracker construction
        """

        _wt = WireTracker(view=self.view, names=wire_name)

        _wt.set_selectability(select)
        _wt.set_selection_nodes(nodes)
        _wt.update(points)

        return _wt

    def update(self):
        """
        Update the curve based on the passed data points
        """

        if self.state == 'UNSELECTED':
            return

        _points = None

        if self.curve['Type'] == 'Spiral':
            _points = self._generate_spiral()

        else:
            _points = self._generate_arc()

        if not _points:
            return

        self.trackers['Curve'][0].update(_points)

    def _generate_spiral(self):
        """
        Generate a spiral curve
        """

        _key = ''
        _rad = 0.0

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
            #otherwise, calcualte a point halfway between.
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

    def _generate_arc(self):
        """
        Generate a simple arc curve
        """

        _start = Vector(self.pi_nodes[0].point)
        _pi = Vector(self.pi_nodes[1].point)
        _end = Vector(self.pi_nodes[2].point)

        _curve = {
                'BearingIn': support.get_bearing(_pi.sub(_start)),
                'BearingOut': support.get_bearing(_end.sub(_pi)),
                'PI': _pi,
                'Radius': self.curve['Radius'],
            }

        self.curve = arc.get_parameters(_curve)

        return arc.get_points(self.curve)

    def _validate_curve(self, curves):
        """
        Given a list of updated curves, validate them against themselves
        and adjoingin geometry
        """

        pass

        #_idx = self.drag.curves[:]

        #if not _idx:
        #    self.is_valid = True
        #    return

        ##append preceding and following curves if first / last curves
        ##aren't being updated
        #if _idx[0] > 0:
        #    _idx.insert(0, _idx[0] - 1)
        #    curves.insert(0, self.curves[_idx[0]])

        #elif _idx[-1] < len(self.curves) - 1:
        #    _idx.append(_idx[-1] + 1)
        #    curves.append(self.curves[_idx[-1]])

        #_styles = [CoinStyle.DEFAULT]*len(curves)

        ##validate curves against each other,
        ##ensuring PI distance >= sum  of curve tangents
        #for _i in range(0, len(curves) - 1):

        #    _c = [curves[_i], curves[_i + 1]]

        #    _tangents = [0.0, 0]

        #    if _c[0]['Type'] == 'Spiral':
        #        _tangents[0] = spiral.get_ordered_tangents(_c[0])[0]

        #    else:
        #        _tangents[0] = _c[0]['Tangent']

        #    if _c[1]['Type'] == 'Spiral':
        #        _tangents[1] = spiral.get_ordered_tangents(_c[1])[1]

        #    else:
        #        _tangents[1] = _c[1]['Tangent']

        #    if (_tangents[0] + _tangents[1])\
        #        > (_c[0]['PI'].distanceToPoint(_c[1]['PI'])):

        #        _styles[_i + 1] = CoinStyle.ERROR
        #        _styles[_i] = CoinStyle.ERROR

        ##do endpoint checks if the first or last curves are changing.
        #_x = []

        ##first curve is updating
        #if _idx[0] == 0:
        #    _x.append(0)

        ##last curve is updating
        #if _idx[-1] == len(self.curves) - 1:
        #    _x.append(-1)

        #for _i in _x:

        #    _c = curves[_i]
        #    _p = self.drag.pi[_i]
        #    _tangent = None

        #    #disable validation for spirals temporarily
        #    if _c['Type'] == 'Spiral':
                
        #        _tans = spiral.get_ordered_tangents(_c)
        #        _tangent = _tans[1]

        #        if _i == 0:
        #            _tangent = _tans[0]

        #    else:
        #        _tangent = _c['Tangent']

        #    if _styles[_i] != CoinStyle.ERROR:

        #        if _tangent > _c['PI'].distanceToPoint(_p):
        #            _styles[_i] = CoinStyle.ERROR

        #for _i, _c in enumerate(curves):
        #    self.trackers['Curves'][_idx[0] + _i].set_style(
        #        _styles[_i]
        #    )

        #self.is_valid = all([_v != CoinStyle.ERROR for _v in _styles])

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
                self.view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        super().finalize()
