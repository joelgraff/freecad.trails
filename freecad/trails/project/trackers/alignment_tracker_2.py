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

from ...geometry import support, arc
from ..support import utils
from .base_tracker import BaseTracker
from .coin_group import CoinGroup
from .coin_style import CoinStyle

from ..support.mouse_state import MouseState
from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

class AlignmentTracker2(BaseTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, doc, view, object_name, alignment):
        """
        Constructor
        """
    
        self.alignment = alignment
        self.callbacks = {}
        self.doc = doc
        self.names = [doc.Name, object_name, 'ALIGNMENT_TRACKER']
        self.mouse = MouseState()

        self.view = view
        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        self.groups = {
            'edit': coin.SoGroup(),
            'drag': coin.SoGroup(),
            'transition': coin.SoGroup(),
            'transform': coin.SoGroup(),
        }

        super().__init__(names=self.names, group=True)

        self.callbacks = {
            'SoLocation2Event':
            self.view.addEventCallback('SoLocation2Event', self.mouse_event),

            'SoMouseButtonEvent':
            self.view.addEventCallback('SoMouseButtonEvent', self.button_event)
        }

        #scenegraph node structure for editing and dragging operations
        self.groups['drag'].addChild(self.groups['transition'])
        self.groups['drag'].addChild(self.groups['transform'])

        self.node.addChild(self.groups['edit'])
        self.node.addChild(self.groups['drag'])

        self.trackers = None

        #generate inital node trackers and wire trackers for mouse interaction
        self.build_trackers()

        #add the tracker geometry to the scenegraph
        for _v in self.trackers['Nodes'] + self.trackers['Wires'] +\
            self.trackers['Curves']:

            self.insert_node(_v.node, self.node)

        #insert in the scenegraph root
        self.insert_node(self.node)

    def mouse_event(self, arg):
        """
        Manage mouse actions affecting multiple nodes / wires
        """

        self.mouse.update(arg, self.view.getCursorPos())

    def button_event(self, arg):
        """
        Manage button actions affecting multiple nodes / wires
        """

        _dragging = self.mouse.button1.dragging or self.mouse.button1.pressed

        #exclusive or - abort if both are true or false
        if not (self.drag_tracker is not None) ^ _dragging:
            return

        pos = self.view.getCursorPos()
        self.mouse.update(arg, pos)

        #if tracker exists, but we're not dragging, shut it down
        if self.drag_tracker:
            self.end_drag(arg, self.view.getPoint(pos))

        elif _dragging:
            self.start_drag(arg, self.view.getPoint(pos))

    def build_trackers(self):
        """
        Build the node and wire trackers that represent the selectable portions of the alignment geometry
        """

        _model = self.alignment.model.data

        #build a list of coordinates from curves in the geometry
        _nodes = [_model['meta']['Start']]

        for _geo in _model['geometry']:

            if _geo['Type'] == 'Curve':
                _nodes += [_geo['PI']]

        _nodes += [_model['meta']['End']]

        #build the trackers
        _names = self.names[:2]
        _result = {'Nodes': [], 'Wires': [], 'Curves': []}

        #node trackers
        for _i, _pt in enumerate(_nodes):

            _tr = NodeTracker(
                view=self.view,
                names=_names + ['NODE-' + str(_i)], point=_pt
            )
            _tr.update(_pt)

            _result['Nodes'].append(_tr)

        #wire trackers - Tangents
        for _i in range(0, len(_result['Nodes']) - 1):

            _nodes = _result['Nodes'][_i:_i + 2]

            _result['Wires'].append(
                self._build_wire_tracker(
                    wire_name=_names + ['WIRE-' + str(_i)],
                    nodes=_nodes,
                    points=[_v.get() for _v in _nodes]
                )
            )

        _curves = self.alignment.get_curves()

        #wire trackers - Curves
        for _i in range(0, len(_result['Wires']) - 1):

            _nodes = _result['Nodes'][_i:_i + 3]

            _points, _x = arc.get_points(_curves[_i])

            _result['Curves'].append(
                self._build_wire_tracker(
                    _names + ['CURVE-' + str(_i)], _nodes, _points, True
                )
            )

        self.trackers = _result

    def _build_wire_tracker(self, wire_name, nodes, points, select=False):
        """
        Convenience function for WireTracker construction
        """

        _wt = WireTracker(view=self.view, names=wire_name)

        _wt.set_selectability(select)
        _wt.set_selection_nodes(nodes)
        _wt.update_points(points)

        return _wt

    def start_drag(self):
        """
        Set up the scene graph for dragging operations
        """

        #get the transitional and transform geometry
        #populate the SoGroup nodes with data points
        #set dragging flags

        _groups = [coin.SoGroup()]*2

        for _v in self.trackers['Nodes'] + self.trackers['Wires'] + \
            self.trackers['Curves']:

            if _v.is_selected():
                _groups[0].addChild(_v.copy())

            elif _v.is_partial():
                _groups[1].addChild(_v.copy())

    def on_drag(self):
        """
        Update method during drag operations
        """

        pass

    def end_drag(self):
        """
        Cleanup method for drag operations
        """

    def finalize(self, node=None):
        """
        Override of the parent method
        """

        self.alignment = None

        if not node:
            node = self.node

        if self.callbacks:
            for _k, _v in self.callbacks.items():
                self.view.removeEventCallback(_k, _v)

        for _v in self.trackers['Nodes'] + self.trackers['Wires']:
            _v.finalize(self.node)

        self.trackers.clear()

        self.remove_node(self.groups['edit'])
        self.remove_node(self.groups['drag'])

        self.groups.clear()

        super().finalize(node)
