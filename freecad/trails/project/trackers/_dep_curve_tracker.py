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
from ..support.drag_state import DragState
from ..support.view_state import ViewState

from .base_tracker import BaseTracker
from .coin_styles import CoinStyles
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
        self.is_valid = True

        self.status_bar = Gui.getMainWindow().statusBar()

        self.drag_lock = ''
        self.drag_reference = 0.0

        #local drag geometry nodes
        self.group = coin.SoSeparator()
        self.drag_coord = coin.SoCoordinate3()

        self.group.addChild(self.drag_coord)

        self.drag_nodes = []
        self.drag_start = []
        self.drag_points = []
        self.drag_arc = None
        self.drag_node = None
        self.drag_style = None
        self.drag_color = None

        #scenegraph node structure for editing and dragging operations
        self.groups = {
            'EDIT': coin.SoGroup(),
            'DRAG': coin.SoGroup(),
        }

        #generate initial node trackers and wire trackers for mouse interaction
        #and add them to the scenegraph
        self.build_trackers(names)

        super().__init__(names=names)

        self.node.addChild(self.groups['EDIT'])
        self.node.addChild(self.groups['DRAG'])

        #insert in the scenegraph root
        self.insert_node(self.node)

    def _update_status_bar(self):
        """
        Update the status bar with the latest mouseover data
        """

        ##self.status_bar.clearMessage()
        #self.status_bar.showMessage(_msg)

        pass

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

        if not DragState().drag_node:
            return

        if not self.name in DragState().drag_node.name:
            return

        if not any([
                _v in DragState().drag_node.name \
                    for _v in ['Start', 'Center', 'End']]):

            return

        if self.drag_reference:
            self._update_curve()

        #if we're still here, the user is attempting to change the curve
        #get the current parameter locks from the UI panel and recalculate

        _vec = self.pi_nodes[1].get().sub(MouseState().coordinates)
        _offset = Vector(self.drag_reference).multiply(_vec.Length)
        _center = self.pi_nodes[1].get().sub(_offset)

        DragState().update(DragState().start, _center)
        DragState().translate_transform.translation.setValue(
            tuple(_center.sub(DragState().start))
        )

        if not self.drag_reference:
            _curve = {
                'Type': self.curve['Type'],
                'BearingIn': self.curve['BearingIn'],
                'BearingOut': self.curve['BearingOut'],
                'PI': self.pi_nodes[1].get(),
                'Center': _center,
                'Delta': self.curve['Delta']
            }

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
        if any([_v in MouseState().component \
            for _v in ['Start', 'Center', 'End']]):

            self.trackers['Curve'][0].state.selected.value = True

    def start_drag(self):
        """
        Override base method
        """

        if not self.state.selected.value:
            return

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
            self.drag_style = _node.getChild(1)
            self.drag_color = _node.getChild(2)

            self.drag_start = [_v.get() for _v in self.pi_nodes]
            self.drag_nodes = [_v for _v in self.pi_nodes if _v.state.dragging]

            #create a partially-complete arc for drag tracking based on
            #the original curve
            self.drag_arc = {
                'BearingIn': self.curve['BearingIn'],
                'BearingOut': self.curve['BearingOut'],
                'PI': self.curve['PI'],
                'Radius': self.curve['Radius'],
                'Tangent': self.curve['Tangent']
            }

            self.insert_node(self.group, 0)

            return

        #no PI nodes are selected, test for selected curve ndoes
        #get the node that's being dragged
        _key = [
            _k for _k in ['Start', 'Center', 'End']\
            if _k in MouseState().component
        ]

        if not _key:
            return

        self.state.dragging = True

        self.drag_reference = \
            self.pi_nodes[1].get().sub(self.curve[_key[0]]).normalize()

        self.trackers['Curve'][0].state.selected.value = True

        self.drag_node = [
            _v for _v in self.trackers['Nodes'] if _v.state.selected.value][0]

        DragState().override = True

    def on_drag(self):
        """
        Override base method
        """

        #abort unselected
        if not self.state.dragging:
            return

        #partially-selected curves will have a drag_idx / drag_nodes.
        #fully-selected / unselected will not
        if self.drag_nodes:

            if DragState().sg_ok:
                self._partial_drag()

            return

        #otherwise, test for curve-editing drag ops
        if self.drag_reference:
            self.validate()

        super().on_drag()

    def _partial_drag(self):
        """
        Perform partial drag if ok
        """

        _pts = []
        _idx = []

        for _i, _v in enumerate(self.pi_nodes):

            if _v.state.dragging:
                _pts.append(Vector(_v.drag_point))
                _idx.append(_i)

            else:
                _pts.append(Vector(_v.point))

        _arc = {
            'BearingIn': self.curve['BearingIn'],
            'BearingOut': self.curve['BearingOut'],
            'PI': _pts[1],
            'Radius': self.curve['Radius'],
            'Direction': self.curve['Direction']
        }

        if 0 in _idx or 1 in _idx:
            _arc['BearingIn'] = support.get_bearing(_pts[1].sub(_pts[0]))

        if 1 in _idx or 2 in _idx:
            _arc['BearingOut'] = support.get_bearing(_pts[2].sub(_pts[1]))


        self.drag_arc = arc.get_parameters(_arc)
        _points = arc.get_points(self.drag_arc, _dtype=tuple)

        self.drag_coord.point.setValues(0, len(_points), _points)

    def end_drag(self):
        """
        Override base implementation
        """

        _arc = None

        #if drag_reference, this is a drag operation on curve nodes
        if self.drag_reference:
            _arc = self.drag_arc

        else:
            #otherwise this is a partial drag at the alignment level
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

        self.state.dragging = False

        if self.drag_start:
            self.remove_node(self.group)
            self.group.removeAllChildren()
            self.drag_coord = None
            self.drag_start = []
            self.drag_nodes = []
            self.drag_arc = None

    def _update_curve(self):
        """
        Update the curve as a result of adjusting it's nodes
        """

        _tpl = None

        for _i, _k in enumerate(['Start', 'Center', 'End']):
            if self.drag_node == self.trackers['Nodes'][_i]:
                _tpl = (_i, _k)

        _point = Vector(self.trackers['Wires'][0].drag_points[_tpl[0]])

        #pre-mpt update, if matrix hasn't updated yet
        if any([math.isnan(_v) for _v in _point]):
            return

        if not ViewState().valid_matrix():
            return

        _arc = {
            'BearingIn': self.curve['BearingIn'],
            'BearingOut': self.curve['BearingOut'],
            'PI': self.pi_nodes[1].get(),
            _tpl[1]: _point,
            'Delta': self.curve['Delta'],
            'Direction': self.curve['Direction']
        }

        if _tpl[1] == 'Start':
            _arc['Tangent'] = \
                Vector(self.trackers['Wires'][0].drag_points[2]).sub(
                    _arc['PI']).Length

        elif _tpl[1] == 'End':
            _arc['Tangent'] = \
                Vector(self.trackers['Wires'][0].drag_points[0]).sub(
                    _arc['PI']).Length

        self.drag_arc = arc.get_parameters(_arc)

        _p = arc.get_points(self.drag_arc)

        self.trackers['Curve'][0].drag_points = [tuple(_v) for _v in _p]

        #update the drag geometry for the wire tracker
        for _i, _k in enumerate(['Start', 'Center', 'End']):

            if _i == _tpl[0]:
                continue

            self.trackers['Wires'][0].drag_points[_i] =\
                self.drag_arc[_k]

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

    def build_trackers(self, names):
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

        #node trackers
        for _i, _pt in enumerate(_coords):

            _name = names[-1] + '-' + _names[_i]

            _tr = NodeTracker(names=names[:2] + [_name], point=_pt)

            _tr.update()
            _tr.conditions.append('!' + names[2])
            _tr.set_visible(False)
            _tr.state.multi_select = False

            _result['Nodes'].append(_tr)

        #wire tracker
        _wt = WireTracker(names[:2] + [names[-1] + '-' + 'Radius'])
        _wt.set_points(nodes=_result['Nodes'])
        _wt.set_selectability(False)
        _wt.state.multi_select = False
        _wt.conditions.append('!' + names[2])
        _wt.set_style(CoinStyles.DASHED)
        _wt.set_visible(False)
        _wt.drag_refresh = False

        _wt.update()

        _result['Wires'].append(_wt)

        _points = []

        #curve wire tracker
        _class = arc

        if self.curve['Type'] == 'Spiral':
            _class = spiral

        _points = _class.get_points(self.curve)

        _wt = WireTracker(names + [self.curve['Type']])
        _wt.set_selectability(True)
        _wt.state.multi_select = False
        _wt.draggable = False
        _wt.drag_override = True

        _wt.set_points(
            points=_points,
            nodes=_result['Nodes'],
            indices=[0, None, -1]
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

        if not self.is_valid:
            self.is_valid = True
            return

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

    def _generate_arc(self, curve=None):
        """
        Generate a simple arc curve
        """

        if curve is None:

            _start = self.pi_nodes[0].get()
            _pi = self.pi_nodes[1].get()
            _end = self.pi_nodes[2].get()

            curve = {
                'BearingIn': support.get_bearing(_pi.sub(_start)),
                'BearingOut': support.get_bearing(_end.sub(_pi)),
                'PI': _pi,
                'Radius': self.curve['Radius'],
            }

        self.curve = arc.get_parameters(curve)

        return arc.get_points(self.curve)

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

        _t = self.drag_arc['Tangent']
        _style = CoinStyles.DEFAULT

        _nodes = []

        for _v in self.pi_nodes:

            if _v.drag_point:
                _nodes.append(Vector(_v.drag_point))

            else:
                _nodes.append(Vector(_v.point))

        #test of left-side tangent validity
        _lt = _nodes[0].sub(_nodes[1]).Length

        print('\n\t',self.name)
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
