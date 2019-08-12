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
from PySide import QtGui
from FreeCAD import Vector

import FreeCADGui as Gui

from ...geometry import support, arc, spiral

from ..support.mouse_state import MouseState
from ..support.drag_state import DragState
from ..support.view_state import ViewState

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
        self.lock_group = None

        self.status_bar = Gui.getMainWindow().statusBar()

        self.drag_lock = ''
        self.drag_reference = 0.0

        #local drag geometry nodes
        self.group = coin.SoSeparator()
        self.drag_coord = coin.SoCoordinate3()

        self.group.addChild(self.drag_coord)

        self.drag_idx = []
        self.drag_nodes = []
        self.drag_start = []
        self.drag_points = []
        self.drag_arc = None

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

    def mouse_event(self, arg):
        """
        Override base function
        """

        super().mouse_event(arg)

        if not self.state.dragging:
            return

        if not DragState().node:
            return

        if not self.name in DragState().node.name:
            return

        if not 'Center' in DragState().node.name:
            return

        #if we're still here, the user is attempting to change the curve
        #get the current paramter locks from the UI panel and recalculate

        _vec = self.pi_nodes[1].get().sub(MouseState().coordinates)
        _offset = Vector(self.drag_reference).multiply(_vec.Length)
        _center = self.pi_nodes[1].get().sub(_offset)

        _curve = {
            'Type': self.curve['Type'],
            'BearingIn': self.curve['BearingIn'],
            'BearingOut': self.curve['BearingOut'],
            'PI': self.pi_nodes[1].get(),
            'Center': _center,
            'Delta': self.curve['Delta']
        }

        DragState().update(DragState().start, _center)
        DragState().translate_transform.translation.setValue(
            tuple(_center.sub(DragState().start))
        )

        self.update(_curve)

        #DO CURVE VALIDATION HERE

    def button_event(self, arg):
        """
        Manage button actions affecting multiple nodes / wires
        """

        if MouseState().button1.state == 'UP':
            return

        #test to see if curve is being dragged by PI nodes
        _sel = [_v.state.selected.value for _v in self.pi_nodes]

        self.state.selected.ignore = False

        if all(_sel) or any(_sel):
            self.state.selected.value = True
            self.state.selected.ignore = True

            return

        #test to see if we're operating on the curve
        _do_select = self.name in MouseState().component

        for _v in self.trackers['Nodes'] + self.trackers['Wires']:

            _v.state.visible.value = _do_select
            _v.state.visible.ignore = _do_select
            _v.refresh()

        self.state.selected.value = _do_select
        self.pi_nodes[1].state.visible.ignore = _do_select
        self.pi_nodes[1].refresh()

        if not _do_select:
            return

        #still here? test for curve node changes
        if 'Center' in MouseState().component:
            self.trackers['Curve'][0].state.selected.value = True

    def start_drag(self):
        """
        Override base method
        """

        #test to see if the curve is being manipulated by it's PI's
        _sel = [_v.state.selected.value for _v in self.pi_nodes]

        #alignment is being dragged, fall back on base implementation
        if all(_sel):
            super().start_drag()
            return

        self.state.dragging = any(_sel)

        #initiate a partial drag and quit if any of the PI nodes are selected
        if self.state.dragging:

            _node = self.trackers['Curve'][0].copy()

            self.group.addChild(_node)
            self.drag_coord = _node.getChild(3)
            self.drag_start = [_v.get() for _v in self.pi_nodes]
            self.drag_idx = [
                _i for _i, _v in enumerate(self.pi_nodes)\
                    if _v.state.selected.value
            ]

            self.drag_nodes = [_v.get() for _v in self.pi_nodes]
            self.drag_arc = {
                'BearingIn':
                support.get_bearing(
                    self.pi_nodes[1].get().sub(self.pi_nodes[0].get())),

                'BearingOut':
                support.get_bearing(
                    self.pi_nodes[2].get().sub(self.pi_nodes[1].get())),

                'PI': self.pi_nodes[1].get(),

                'Radius': self.curve['Radius']
            }

            self.insert_node(self.group, 0)

            return

        #no PI nodes are selected, test for selected curve ndoes
        self.drag_reference = \
            self.pi_nodes[1].get().sub(self.curve['Center']).normalize()

        DragState().override = True

    def on_drag(self):
        """
        Override base method
        """

        #need to update partially-selected curves
        #and do curve validations

        #abort unselected
        if not self.state.dragging:
            return

        #partially-selected wires will have a drag_idx.
        #fully-selected / unselected will not
        if self.drag_nodes:

            if DragState().sg_ok:
                self._partial_drag()

            return

        #NEED TO VALIDATE THE CURVE CHANGES

        super().on_drag()

    def _partial_drag(self):
        """
        Perform partial drag if ok
        """

        _drag_pts = []

        for _i in self.drag_idx:
            _drag_pts.append(self.drag_nodes[_i])

        #transform the selected PI nodes by the current drag transformation
        _drag_pts = self.transform_points(_drag_pts, DragState().node_group)

        _points = self.drag_nodes[:]

        _j = 0

        for _i in self.drag_idx:
            _points[_i] = _drag_pts[_j]
            _j += 1

        if any([_i in self.drag_idx for _i in [0, 1]]):
            self.drag_arc['BearingIn'] = \
                support.get_bearing(_points[1].sub(_points[0]))

        if any([_i in self.drag_idx for _i in [1, 2]]):
            self.drag_arc['BearingOut'] = \
                    support.get_bearing(_points[2].sub(_points[1]))

        if 1 in self.drag_idx:
            self.drag_arc['PI'] = _points[1]

        _arc = arc.get_parameters(self.drag_arc)
        _points = arc.get_points(_arc)

        self.drag_coord.point.setValues(0, len(_points),_points)

    def end_drag(self):
        """
        Override base implementation
        """

        _pts = [_v.get() for _v in self.pi_nodes]

        _arc = {
            'BearingIn': support.get_bearing(_pts[1].sub(_pts[0])),
            'BearingOut': support.get_bearing(_pts[2].sub(_pts[1])),
            'PI': _pts[1],
            'Radius': self.curve['Radius']
        }

        self.curve = arc.get_parameters(_arc)

        _points = arc.get_points(self.curve)

        self.trackers['Curve'][0].update(_points)

        self.rebuild_trackers()

        if self.drag_idx:
            self.remove_node(self.group)
            self.group.removeAllChildren()
            self.drag_coord = None
            self.drag_start = []
            self.drag_idx = []
            self.drag_nodes = []
            self.drag_arc = None

    def rebuild_trackers(self):
        """
        Rebuild the existing trackers to match updated curve
        """

        #build a list of coordinates from curves in the geometry
        #skipping the last (duplicate of center)
        _coords = [self.curve[_k] for _k in ['Start', 'Center', 'End']]

        #rebuild all nodes
        for _i, _v in enumerate(_coords):
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
        _wt.state.multi_select = False
        #_wt.state.draggable = False

        _wt.set_points(
            points=_points,
            nodes=[_result['Nodes'][0], _result['Nodes'][-1]]
        )

        _result['Curve'] = [_wt]

        self.trackers = _result
        self._build_edit_group()
        self.update()

    def update(self, curve=None):
        """
        Update the curve based on the passed data points
        """

        #if not self.state.selected.value:
        #    return

        _points = None

        if curve is None:
            curve = self.curve

        if curve['Type'] == 'Spiral':
            _points = self._generate_spiral()

        else:
            _points = self._generate_arc(curve)

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

    def _generate_arc(self, curve=None):
        """
        Generate a simple arc curve
        """

        if curve is None:

            _start = Vector(self.pi_nodes[0].point)
            _pi = Vector(self.pi_nodes[1].point)
            _end = Vector(self.pi_nodes[2].point)

            curve = {
                'BearingIn': support.get_bearing(_pi.sub(_start)),
                'BearingOut': support.get_bearing(_end.sub(_pi)),
                'PI': _pi,
                'Radius': self.curve['Radius'],
            }

        self.curve = arc.get_parameters(curve)

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
