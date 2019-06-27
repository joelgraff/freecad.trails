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

from ...geometry import support, arc

from .base_tracker import BaseTracker
from .coin_style import CoinStyle

from ..support.mouse_state import MouseState
from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

class AlignmentTracker(BaseTracker):
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
        self.curves = []
        self.names = [doc.Name, object_name, 'ALIGNMENT_TRACKER']
        self.mouse = MouseState()
        self.user_dragging = False
        self.is_valid = True
        self.status_bar = Gui.getMainWindow().statusBar()

        self.drag_geometry = {
            'Start': Vector(),
            'Indices': [],
            'Nodes': [],
            'Wires': [],
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
            'SELECTED': coin.SoSeparator(),
            'PARTIAL': coin.SoSeparator(),
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

        _id = ''

        if info:
            _id = info['Component']

        _msg = _id + ' ' + str(tuple(self.view.getPoint(self.mouse.pos)))

        #self.status_bar.clearMessage()
        self.status_bar.showMessage(_msg)

    def mouse_event(self, arg):
        """
        Manage mouse actions affecting multiple nodes / wires
        """

        _p = self.view.getCursorPos()

        self.mouse.update(arg, _p)

        self._update_status_bar(self.view.getObjectInfo(_p))

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

        self.drag_geometry['Start'] = self.view.getPoint(self.mouse.pos)

        #create list of selected and partially-selected wires
        _wires = [
            _v for _v in self.trackers['Tangents'] + self.trackers['Curves']\
                if _v.state != 'UNSELECTED'
        ]

        #iterate, adding scene nodes to appropriate groups
        for _w in _wires:
            self.groups[_w.state].addChild(_w.copy())

        self.curves = self.alignment.get_curves()

        _idx = []

        #store the wire tracker and it's index
        _partial = [
            _i for _i, _v in enumerate(self.trackers['Tangents'])\
                if _v.state == 'PARTIAL'
        ]

        _selected = [
            _i for _i, _v in enumerate(self.trackers['Tangents'])\
                if _v.state == 'SELECTED'
        ]

        print('parital = ', _partial)
        print('selected = ', _selected)

        #if only an endpoint was picked, add the adjacent tangent
        if len(_partial) == 1:

            if _partial[0] == 0:
                _partial.append(1)

            else:
                _partial.insert(0, _partial[0] - 1)

        #otherwise, add the preceeding and following tangents
        else:

            if _partial[0] > 0:
                _partial.insert(0, _partial[0] - 1)

            if _partial[-1] < len(self.trackers['Tangents']) - 1:
                _partial.append(_partial[-1] + 1)


        #save the tangents that are used to update the affected curves
        self.drag_geometry['Wires'] =\
            self.trackers['Tangents'][_partial[0]:_partial[-1] + 1]

        #save the list of tangent indices
        self.drag_geometry['Indices'] = _partial

        #save the node trackers
        self.drag_geometry['Nodes'] = [
            _w for _v in self.drag_geometry['Wires']\
                for _w in _v.selection_nodes if _w.state == 'SELECTED'
        ]

        #store the entire list of curve goemetry for efficiency
        self.drag_geometry['Curves'] = self.alignment.get_curves()

    def on_drag(self):
        """
        Update method during drag operations
        """

        _world_pos = self.view.getPoint(self.mouse.pos)

        self._update_transform(_world_pos)

        self._update_pi_nodes(_world_pos)

        _curves = self._generate_curves()

        self._validate_curves(_curves)

    def end_drag(self):
        """
        Cleanup method for drag operations
        """

        if self.is_valid:
            self.alignment.update_curves(self.drag_geometry['Curves'])

        #clear the drag_geometry dict
        for _v in self.drag_geometry.values():

            if isinstance(_v, Vector):
                _v =Vector()
            else:
                _v.clear()

        #remove child nodes from the selected group
        self.groups['SELECTED'].removeAllChildren()
        self.groups['SELECTED'].addChild(self.drag_transform)

        #remove child nodes from the partial group
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

    def _update_transform(self, pos):
        """
        Update the transform node for selected geometry
        """

        _pos = tuple(pos.sub(self.drag_geometry['Start']))

        self.drag_transform.translation.setValue(_pos)

    def _update_pi_nodes(self, world_pos):
        """
        Internal function - Update points of intersection
        """

        #update nodes that connect selected elements back to unslected
        for _v in self.drag_geometry['Nodes']:
            _v.update(world_pos)

        for _v in self.drag_geometry['Wires']:
            _v.update([_w.get() for _w in _v.selection_nodes])

    def _transform_nodes(self, nodes):
        """
        Transform selected nodes by the transformation matrix
        """

        _matrix = self.get_matrix()
        _result = []

        for _n in nodes:

            _v = tuple(_n.get())

            if _n.state == 'SELECTED':
                _v = coin.SbVec4f(_v + (1.0,))
                _v = _matrix.multVecMatrix(_v).getValue()[:3]

            _result.append(Vector(_v))

        return _result

    def _generate_curves(self):
        """
        Internal function - Generate curves based on existing curves and nodes
        """

        _curves = self.drag_geometry['Curves']
        _tgts = self.drag_geometry['Wires']
        _indices = self.drag_geometry['Indices']
        _result = []

        _rng = range(0, len(_tgts) - 1)

        for _i in _rng:

            #must transform nodes of fully-selected tangents!

            _start = _tgts[_i].selection_nodes[0].get()
            _pi = _tgts[_i].selection_nodes[1].get()
            _end = _tgts[_i + 1].selection_nodes[1].get()

            #_nodes = self._transform_nodes( [_pi, _end]
            #    _tgts[_i].selection_nodes[1:] + _tgts[_i + 1].selection_nodes,
            #)

            #print(_nodes)

            _tst = _pi.sub(_start)
            _tend = _end.sub(_pi)

            _idx = _indices[_i]

            _curve = arc.get_parameters(
                {
                    'BearingIn': support.get_bearing(_tst),
                    'BearingOut': support.get_bearing(_tend),
                    'PI': _pi,
                    'Radius': _curves[_idx]['Radius'],
                }
            )

            _points, _x = arc.get_points(_curve)

            #save a reference to the tracker for later validation and update
            _curve['tracker'] = self.trackers['Curves'][_idx]
            _curve['tracker'].update(_points)

            self.drag_geometry['Curves'][_idx] = _curve

            _result.append(_curve)

        #add adjoining curve if only one curve is being updated in a
        #multi-curve alignment (first or last curve is being updated)
        if (_rng.stop - _rng.start == 1) and  len(_curves) > 1:

            _c = _curves[1]
            _c['tracker'] = self.trackers['Curves'][-2]

            if _indices[0] != 0:
                _c = _curves[-2]
                _result.insert(0, _c)
            else:
                _result.append(_c)

        return _result

    def _validate_curves(self, curves):
        """
        Internal function - Validate curves, set styles to indicate errors
        """

        #1. Create a list of pairs, starting at the curve preceeding the
        #   first new curve

        #2. Iterate the pairs testing for distance between PI's exceeding
        #   sum of adjoining curve tangents, or single curve tangent exceeding
        #   distance between PI and start / end of alignment, if applicable

        _indices = self.drag_geometry['Indices']

        _styles = [CoinStyle.DEFAULT]*len(curves)

        for _i in range(0, len(curves) - 1):

            _c = [curves[_i], curves[_i + 1]]

            if (_c[0]['Tangent'] + _c[1]['Tangent'])\
                > (_c[0]['PI'].distanceToPoint(_c[1]['PI'])):

                _styles[_i + 1] = CoinStyle.ERROR
                _styles[_i] = CoinStyle.ERROR

        #if only two tangents are being used, we need to do endpoint
        #checks as this can only happen if the endpoint is selected,
        #or the alignment only has two tangents

        _idx = []

        if _indices[0] == 0:
            _idx.append(0)

        if _indices[-1] == len(self.trackers['Nodes']) - 2:
            _idx.append(-1)

        for _i in _idx:

            _c = curves[_i]
            _p = self.trackers['Nodes'][_i].get()

            if _styles[_i] != CoinStyle.ERROR:

                if _c['Tangent'] > _c['PI'].distanceToPoint(_p):
                    _styles[_i] = CoinStyle.ERROR

        for _i, _c in enumerate(curves):
            _c['tracker'].set_style(_styles[_i])

        self.is_valid = all([_v != CoinStyle.ERROR for _v in _styles])

    def finalize(self, node=None, parent=None):
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

            for _v in self.trackers.values():
                _t.extend(_v)

            for _v in _t:
                _v.finalize(self.node)

            self.trackers.clear()

        if self.groups:
            for _v in self.groups.values():
                self.remove_node(_v)

            self.groups.clear()

        super().finalize(node, parent)
