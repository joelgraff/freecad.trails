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
        self.user_dragging = False
        self.drag_geometry = {
            'Nodes': [],
            'Curves':[],
        }

        self.view = view
        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        super().__init__(names=self.names, group=True)

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
            'SELECTED': coin.SoGroup(),
            'PARTIAL': coin.SoGroup(),
        }

        self.drag_transform = coin.SoTransform()

        self.groups['SELECTED'].addChild(self.drag_transform)

        self.groups['DRAG'].addChild(self.groups['SELECTED'])
        self.groups['DRAG'].addChild(self.groups['PARTIAL'])

        self.node.addChild(self.groups['EDIT'])
        self.node.addChild(self.groups['DRAG'])

        #generate inital node trackers and wire trackers for mouse interaction
        #and add them to the scenegraph
        self.trackers = None
        self.build_trackers()

        _trackers = []
        [_trackers.extend(_v) for _v in self.trackers.values()]

        for _v in _trackers:
            self.insert_node(_v.node, self.groups['EDIT'])

        #insert in the scenegraph root
        self.insert_node(self.node)

    def mouse_event(self, arg):
        """
        Manage mouse actions affecting multiple nodes / wires
        """

        self.mouse.update(arg, self.view.getCursorPos())

        if self.mouse.button1.dragging:

            if self.user_dragging:
                self.on_drag()
                self.view.redraw()

            else:
                self.start_drag()
                self.user_dragging = True

        #should not be necessary, but included here in case
        #an event gets missed
        elif self.user_dragging:
            self.end_drag()
            self.user_dragging = False

    def button_event(self, arg):
        """
        Manage button actions affecting multiple nodes / wires
        """

        self.mouse.update(arg, self.view.getCursorPos())

        #terminate dragging if button is released
        if self.user_dragging and not self.mouse.button1.dragging:
            self.end_drag()
            self.user_dragging = False

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
        _result = {'Nodes': [], 'Tangents': [], 'Curves': []}

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

            _result['Tangents'].append(
                self._build_wire_tracker(
                    wire_name=_names + ['WIRE-' + str(_i)],
                    nodes=_nodes,
                    points=[_v.get() for _v in _nodes]
                )
            )

        _curves = self.alignment.get_curves()

        #wire trackers - Curves
        for _i in range(0, len(_result['Tangents']) - 1):

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
        _wt.update(points)

        return _wt

    def start_drag(self):
        """
        Set up the scene graph for dragging operations
        """

        #create list of selected and partially-selected wires
        _wires = [
            _v for _v in self.trackers['Tangents'] + self.trackers['Curves']\
                if _v.state != 'UNSELECTED'
        ]

        #iterate, adding scene nodes to appropriate groups
        #and storng a list of selected nodes in partially-selected wires
        for _w in _wires:
            self.groups[_w.state].addChild(_w.copy())

        #create list of nodes which are 'connecting' geometry to non-selected
        #geometry
        _curves = self.alignment.get_curves()

        _idx = []

        #iterate tangents, selecting only the partial ones
        for _i, _v in enumerate(self.trackers['Tangents']):

            if _v.state != 'PARTIAL':
                continue

            #add the tangent and select the curves on either side of it
            self.drag_geometry['Nodes'].append(_v)

            _l = [_i - 1, _i]

            if _i == 0:
                _l = [_l[1]]

            elif _i == len(self.trackers['Tangents']) - 1:
                _l = [_l[0]]

            _idx.extend([_i for _i in _l if _i not in _idx])

        self.drag_geometry['Curves'] = [
            (_i, _curves[_i]['Radius']) for _i in _idx
        ]

        print(self.drag_geometry['Curves'])

    def on_drag(self):
        """
        Update method during drag operations
        """

        #update nodes that connect selected elements back to unslected
        _world_pos = self.view.getPoint(self.mouse.pos)

        for _v in self.drag_geometry['Nodes']:

            for _w in \
                [_w for _w in _v.selection_nodes if _w.state == 'SELECTED']:

                _w.update(_world_pos)

            _v.update([_w.get() for _w in _v.selection_nodes])

        _nodes = self.trackers['Nodes']
        _new_curves = []

        #update the curve geometry
        for _i, _t in enumerate(self.drag_geometry['Curves']):

            _tst = _nodes[_t[0] + 1].get().sub(_nodes[_t[0]].get())
            _tend = _nodes[_t[0] + 2].get().sub(_nodes[_t[0] + 1].get())

            _curve = arc.get_parameters (
                {
                    'BearingIn': support.get_bearing(_tst),
                    'BearingOut': support.get_bearing(_tend),
                    'PI': _nodes[_t[0] + 1].get(),
                    'Radius': _t[1],
                }
            )

            _points, _x = arc.get_points(_curve)

            self.trackers['Curves'][_i].update(_points)

            _new_curves.append(_curve)

        #check for errors, first between the curves
        _pairs = [[_i, _i + 1] for _i in range(0, len(_new_curves) - 1)]

        #if the sum of the curve tangent lengths eceeds the distance between
        #the points, then they overlap
        _t_curves = self.trackers['Curves']
        _t_states = [CoinStyle.DEFAULT]*len(_t_curves)

        for _i in _pairs:

            _p = [_new_curves[_j] for _j in _i]

            if (_p[0]['Tangent'] + _p[1]['Tangent'])\
                > (_p[0]['PI'].distanceToPoint(_p[1]['PI'])):

                for _j in _i:
                    _t_states[_j] = CoinStyle.ERROR

        #test for error in end curves and points
        for _i in [0, -1]:

            _c = _new_curves[_i]
            _p = self.trackers['Nodes'][_i].get()

            if _t_states[_i] != CoinStyle.ERROR:

                if _c['Tangent'] > _c['PI'].distanceToPoint(_p):
                    _t_states[_i] = CoinStyle.ERROR


        #update styles
        for _i, _v in enumerate(_t_states):
            _t_curves[_i].set_style(_v)

    def end_drag(self):
        """
        Cleanup method for drag operations
        """

        self.drag_geometry = {'Nodes': [], 'Curves': []}

        _rng = range(1, self.groups['SELECTED'].getNumChildren())

        for _i in _rng:
            self.groups['SELECTED'].removeChild(_i)

        self.groups['PARTIAL'].removeAllChildren()

    def get_matrix(self):
        """
        Return the transformation matrix for the provided node
        """

        _sel_group = self.groups['SELECTED']

        #only one child node means no geometry
        if _sel_group.getNumChildren() < 2:
            return None

        #define the search path
        _search = coin.SoSearchAction()
        _search.setNode(_sel_group.getChild(2))
        _search.apply(self.view.getSceneGraph())

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(self.viewport)
        _matrix.apply(_search.getPath())

        return _matrix.getMatrix()

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

        if self.trackers:
            _t = []
            [_t.extend(_v) for _v in self.trackers.values()]

            for _v in _t:
                _v.finalize(self.node)

            self.trackers.clear()

        if self.groups:
            for _v in self.groups.values():
                self.remove_node(_v)

            self.groups.clear()

        super().finalize(node)
