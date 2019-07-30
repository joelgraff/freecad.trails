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

from pivy import coin

from FreeCAD import Vector

import FreeCADGui as Gui

from ...geometry import support

from .base_tracker import BaseTracker

from ..support.utils import Constants as C
from ..support.mouse_state import MouseState
from ..support.view_state import ViewState

from ..containers import DragState

from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

class AlignmentBaseTestTracker(BaseTracker):
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
        self.datum = alignment.model.data['meta']['Start']

        self.drag = DragState()

        #base (placement) transformation for the alignment
        self.transform = coin.SoTransform()
        self.transform.translation.setValue(
            tuple(alignment.model.data['meta']['Start'])
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

    def mouse_event(self, arg):
        """
        Manage mouse actions affecting multiple nodes / wires
        """

        pass

    def button_event(self, arg):
        """
        Override base button actions
        """

        pass

    def build_trackers(self):
        """
        Build the node and wire trackers that represent the selectable
        portions of the alignment geometry
        """

        _model = self.alignment.model.data

        #build a list of coordinates from curves in the geometry
        _nodes = [Vector()]

        for _geo in _model['geometry']:

            if _geo['Type'] != 'Line':
                _nodes += [_geo['PI']]

        _nodes += [_model['meta']['End']]

        #build the trackers
        _names = self.names[:2]
        _result = {'Nodes': [], 'Tangents': [], 'Curves': []}

        #node trackers
        for _i, _pt in enumerate(_nodes):

            _tr = NodeTracker(names=_names + ['NODE-' + str(_i)], point=_pt)
            _result['Nodes'].append(_tr)

        _result['Nodes'][0].is_end_node = True
        _result['Nodes'][-1].is_end_node = True

        #wire trackers - Tangents
        for _i in range(0, len(_result['Nodes']) - 1):

            _nodes = _result['Nodes'][_i:_i + 2]

            _result['Tangents'].append(
                self._build_wire_tracker(
                    wire_name=_names + ['WIRE-' + str(_i)],
                    nodes=_nodes,
                    points=[_v.get() for _v in _nodes],
                    select=True
                )
            )

        _curves = self.alignment.get_curves()
        _names = self.names[:2]

        self.trackers = _result

    def _build_wire_tracker(self, wire_name, nodes, points, select=False):
        """
        Convenience function for WireTracker construction
        """

        _wt = WireTracker(names=wire_name)

        _wt.set_selectability(select)
        _wt.set_selection_nodes(nodes)
        _wt.update(points)

        return _wt

    def set_selectability(self, is_selectable):
        """
        Override of the base implementation
        """

        pass

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
        _search.setNode(_sel_group.getChild(1))
        _search.apply(ViewState().sg_root)

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(ViewState().viewport)
        _matrix.apply(_search.getPath())

        return _matrix.getMatrix()

    def _update_transform(self, pos, do_rotation, modify):
        """
        Update the transform node for selected geometry
        """

        _scale = 1.0

        if modify:
            _scale = 0.10

        if do_rotation:

            self.drag_transform.rotation = \
                self._update_rotation(pos.sub(self.drag.center), modify)

            _vec = pos.sub(Vector(self.drag_transform.translation.getValue()))
            self.drag.start = _vec

        else:

            _vec = pos.sub(self.drag.position).multiply(_scale)
            self.drag.translation = self.drag.translation.add(_vec)

            self.drag_transform.translation.setValue(
                tuple(self.drag.translation)
            )

    def _update_rotation(self, vector, modify=False):
        """
        Manage rotation during dragging
        """

        _angle = support.get_bearing(vector)

        if self.drag.rotation is None:

            self.drag_transform.center.setValue(
                coin.SbVec3f(tuple(self.drag.center))
            )

            _nodes = [_v.get() \
                for _v in self.trackers['Nodes'] if _v.state.selected.value]

            _nodes = [_v.sub(_nodes[0]) for _v in _nodes]

            _avg = Vector()

            for _v in _nodes:
                _avg = _avg.add(_v)

            _avg.multiply(1 / len(_nodes)).normalize()

            self.drag.rotation = 0.0
            self.drag.angle = _angle

        _scale = 1.0

        if modify:
            _scale = 0.10

        _delta = self.drag.angle - _angle

        if _delta < -math.pi:
            _delta += C.TWO_PI

        elif _delta > math.pi:
            _delta -= C.TWO_PI

        self.drag.rotation += _delta * _scale
        self.drag.angle = _angle

        #return the +z axis rotation for the transformation
        return coin.SbRotation(coin.SbVec3f(0.0, 0.0, 1.0), self.drag.rotation)

    def _update_pi_nodes(self, world_pos):
        """
        Internal function - Update wires with selected nodes
        """

        _tans = self.trackers['Tangents']

        #transform selected nodes
        _result = self._transform_nodes(self.drag.nodes)

        #write updated nodes to PI's
        for _i, _v in enumerate(_result):

            #pi index
            _j = self.drag.node_idx[_i]

            #save the updated PI coordinate
            self.trackers['Nodes'][_j].point = _v

            _limits = [_w if _w >= 0 else 0 for _w in [_j - 1, _j + 1]]

            #if there are partially selected tangents, we need to manually
            #update the scenegraph for the selected vertex
            for _l, _t in enumerate(_tans[_limits[0]:_limits[1]]):

                if _t.state.selected._value != self.State.SELECT_PARTIAL:
                    continue

                _pts = [tuple(_w.get()) for _w in _t.selection_nodes]

                if _t.selection_nodes[0].state.selected.value:
                    _pts[0] = tuple(_v)

                else:
                    _pts[1] = tuple(_v)

                self.groups['PARTIAL'].getChild(_l).getChild(4)\
                    .point.setValues(_pts)

    def _transform_nodes(self, nodes):
        """
        Transform selected nodes by the transformation matrix
        """

        _matrix = self.get_matrix()
        _result = []

        for _n in nodes:

            _v = coin.SbVec4f(tuple(_n) + (1.0,))
            _v = _matrix.multVecMatrix(_v).getValue()[:3]

            _result.append(Vector(_v).sub(self.datum))

        return _result

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
