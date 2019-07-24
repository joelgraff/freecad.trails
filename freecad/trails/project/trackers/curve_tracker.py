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

from .base_tracker import BaseTracker, TriState
from .coin_style import CoinStyle

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

        self.show_conditions = []
        self.coin_style = None
        self.curve = curve
        self.pi_nodes = pi_nodes
        self.callbacks = {}
        self.name = names
        self.mouse = MouseState()
        self.user_dragging = False
        self.is_valid = True
        self.status_bar = Gui.getMainWindow().statusBar()
        self.drag = DragState()
        self.view = view
        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        self.node_names = ['Center', 'Start', 'End', 'PI', 'Center']
        self.wire_names = (
            ('Start Radius', 1, 0),
            ('Start Tangent', 1, 3),
            ('End Radius', 2, 0),
            ('End Tangent', 2, 3)
        )

        super().__init__(names=self.name)

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
            self.insert_node(_v.switch, self.groups['EDIT'])

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

    def set_style(self, style):
        """
        Override of base function
        """

        self.trackers['Curve'][0].set_style(style)

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

        _p = self.view.getCursorPos()

        self.mouse.update(arg, _p)

        if self.mouse.button1.state != 'UP':
            return

        _info = self.view.getObjectInfo(_p)
        _selected = TriState.OFF

        #if the curve is picked, set state to selected
        if _info:
            if self.name[2] in _info['Component']:
                _selected = TriState.ON

        #if change in selection state, trackers will be visible if
        #new state is selected
        if _selected != self.state.selected:

            self.state.selected = _selected
            self.trackers['Curve'][0].override.selected = _selected

            if _selected == TriState.OFF:
                _selected = TriState.UNDEFINED

            #always show trackers if necessary
            for _v in self.trackers['Nodes'] + self.trackers['Wires']:
                _v.override.visible = _selected

        #disable the curve PI when the curve is selected
        if self.is_selected():
            self.pi_nodes[1].override.visible = TriState.OFF

            for _v in self.trackers['Nodes'] + self.trackers['Wires']:
                _v.on()

        else:
            #force refresh of nodes and trackers
            self.pi_nodes[1].on()
            self.pi_nodes[1].override.visible = TriState.UNDEFINED

            for _v in self.trackers['Nodes'] + self.trackers['Wires']:
                _v.off()

    def rebuild_trackers(self):
        """
        Rebuild the existing trackers to match updated curve
        """

        #build a list of coordinates from curves in the geometry
        #skipping the last (duplicate of center)
        _coords = [self.curve[_k] for _k in self.node_names[:-1]]

        for _i, _v in enumerate(_coords[:-1]):
            self.trackers['Nodes'][_i].update(_v)

        for _i, _v in enumerate(self.wire_names):
            self.trackers['Wires'][_i].update([_coords[_v[1]], _coords[_v[2]]])

    def build_trackers(self):
        """
        Build the node and wire trackers that represent the selectable
        portions of the curve geometry
        """

        #build a list of coordinates from curves in the geometry
        #skipping the last (duplicate of center)
        _coords = [self.curve[_k] for _k in self.node_names[:-1]]

        #build the trackers
        _result = {'Nodes': [], 'Wires': [], 'Curve': None}

        #node trackers - don't create a PI node
        for _i, _pt in enumerate(_coords[:-1]):

            _names = self.name[:]
            _names[-1] = _names[-1] + '-' + self.node_names[_i]

            _tr = NodeTracker(
                view=self.view,
                names=_names,
                point=_pt
            )

            _tr.update(_pt)
            _tr.conditions.append('!' + self.name[2])
            _tr.off()

            _result['Nodes'].append(_tr)

        #wire trackers
        for _i, _v in enumerate(self.wire_names):

            _names = self.name[:]
            _names[-1] = _names[-1] + '-' + _v[0]

            _wt = self._build_wire_tracker(
                wire_name=_names,
                nodes=_result['Nodes'],
                points=[_coords[_v[1]], _coords[_v[2]]]
            )

            _wt.conditions.append('!' + self.name[2])
            _wt.set_style(CoinStyle.EDIT)
            _wt.off()
            _result['Wires'].append(_wt)

        _points = []

        #curve wire tracker
        _class = arc

        if self.curve['Type'] == 'Spiral':
            _class = spiral

        _points = _class.get_points(self.curve)

        _result['Curve'] = [
            self._build_wire_tracker(
                wire_name=self.name + [self.curve['Type']],
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

        if not self.is_selected():
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

        print('finailizing curve tracker')
        super().finalize()
