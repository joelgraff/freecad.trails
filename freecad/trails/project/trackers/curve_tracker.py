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

from ..support.mouse_state import MouseState

from .base_tracker import BaseTracker
from .coin_style import CoinStyle
from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

class CurveTracker(BaseTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, names, curve, pi_nodes):
        """
        Constructor
        """

        self.curve = curve
        self.pi_nodes = pi_nodes
        self.trackers = None

        self.status_bar = Gui.getMainWindow().statusBar()

        super().__init__(names=names)

        #scenegraph node structure for editing and dragging operations
        self.groups = {
            'EDIT': coin.SoGroup(),
            'DRAG': coin.SoGroup(),
        }

        self.node.addChild(self.groups['EDIT'])
        self.node.addChild(self.groups['DRAG'])

        #generate initial node trackers and wire trackers for mouse interaction
        #and add them to the scenegraph
        self.build_trackers()

        #insert in the scenegraph root
        self.insert_node(self.node)

    def _update_status_bar(self):
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

    def _build_edit_group(self):
        """
        Build / rebuild the edit group node and the tracker nodes that
        belong in it.
        """

        _node = self.groups['EDIT']
        _node.removeAllChildren()

        _trackers = []

        for _v in self.trackers.values():
            _trackers.extend(_v)

        for _v in _trackers:
            self.insert_node(_v.switch, _node)

    def set_base_style(self, style=None):
        """
        Override of base function
        """

        self.trackers['Curve'][0].set_base_style(style)
        super().set_base_style(style)

    def set_style(self, style=None):
        """
        Override of base function
        """

        if not self.trackers:
            return

        self.trackers['Curve'][0].set_style(style)
        super().set_style(style)

    def button_event(self, arg):
        """
        Manage button actions affecting multiple nodes / wires
        """

        if MouseState().button1.state == 'UP':
            return

        _do_select = self.name in MouseState().component

        for _v in self.trackers['Nodes'] + self.trackers['Wires']:

            _v.state.visible.value = _do_select
            _v.state.visible.ignore = _do_select
            _v.refresh()

        self.state.selected.value = _do_select

    def rebuild_trackers(self):
        """
        Rebuild the existing trackers to match updated curve
        """

        #build a list of coordinates from curves in the geometry
        #skipping the last (duplicate of center)
        _coords = [self.curve[_k] for _k in ['Start', 'Center', 'End']]

        #rebuild all nodes except for the PI
        for _i, _v in enumerate([_coords[0], _coords[-1]]):
            self.trackers['Nodes'][_i].update(_v)

        self.trackers['Wires'][0].update(_coords)

        self._build_edit_group()

    def build_trackers(self):
        """
        Build the node and wire trackers that represent the selectable
        portions of the curve geometry
        """
        _names = ['Start', 'Center', 'End']

        if self.curve['Type'] == 'Spiral':
            _names = ['Start', 'End']

        #build a list of coordinates from curves in the geometry
        #skipping the last (duplicate of center)
        _coords = [self.curve[_k] for _k in _names]

        #build the trackers
        _result = {'Nodes': [], 'Wires': [], 'Curve': None}

        #node trackers - don't create a PI node
        for _i, _pt in enumerate(_coords):

            _name = self.names[-1] + '-' + _names[_i]

            _tr = NodeTracker(names=self.names[:2] + [_name], point=_pt)

            _tr.update()
            _tr.conditions.append('!' + self.names[2])
            _tr.set_visible(False)
            _tr.state.multi_select = False

            _result['Nodes'].append(_tr)

        #wire tracker
        _wt = WireTracker(self.names[:2] + [self.names[-1] + '-' + 'Radius'])
        _wt.set_points(nodes=_result['Nodes'])
        _wt.set_selectability(False)
        _wt.state.multi_select = False
        _wt.conditions.append('!' + self.names[2])
        _wt.set_style(CoinStyle.EDIT)
        _wt.set_visible(False)

        _wt.update()

        _result['Wires'].append(_wt)

        _points = []

        #curve wire tracker
        _class = arc

        if self.curve['Type'] == 'Spiral':
            _class = spiral

        _points = _class.get_points(self.curve)

        _wt = WireTracker(self.names + [self.curve['Type']])

        _wt.set_selectability(True)

        _wt.set_points(
            points=_points, 
            nodes=[_result['Nodes'][0], _result['Nodes'][-1]]
        )

        _wt.state.multi_select = False

        _wt.update()

        _result['Curve'] = [_wt]

        self.trackers = _result
        self._build_edit_group()

    def update(self):
        """
        Update the curve based on the passed data points
        """

        #if not self.state.selected.value:
        #    return

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

    def set_selectability(self, is_selectable):
        """
        Override of base implementation
        """

        for _v in self.trackers['Nodes'] + self.trackers['Curve']:

            _v.set_selectability(is_selectable)

    def finalize(self):
        """
        Cleanup the tracker
        """

        for _t in self.trackers.values():

            for _u in _t:
                _u.finalize()

        self.remove_node(self.groups['EDIT'], self.node)
        self.remove_node(self.groups['DRAG'], self.node)

        super().finalize()
