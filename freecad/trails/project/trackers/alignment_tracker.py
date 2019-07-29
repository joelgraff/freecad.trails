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

from ...geometry import support, spiral

from .base_tracker import BaseTracker
from .coin_style import CoinStyle

from ..support.utils import Constants as C
from ..support.mouse_state import MouseState

from ..containers import DragState

from .node_tracker import NodeTracker
from .wire_tracker import WireTracker
from .curve_tracker import CurveTracker

class AlignmentTracker(BaseTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, doc, view, object_name, alignment, datum=Vector()):
        """
        Constructor
        """

        self.alignment = alignment
        self.callbacks = {}
        self.doc = doc
        self.curves = []
        self.names = [doc.Name, object_name, 'ALIGNMENT_TRACKER']
        self.user_dragging = False
        self.is_valid = True
        self.status_bar = Gui.getMainWindow().statusBar()
        self.pi_list = []
        self.datum = alignment.model.data['meta']['Start']

        self.drag = DragState()

        self.view = view
        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        #base (placement) transformation for the alignment
        self.transform = coin.SoTransform()
        self.transform.translation.setValue(
            tuple(alignment.model.data['meta']['Start'])
        )
        super().__init__(
            view=view, names=self.names, children=[self.transform]
        )

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

        self._update_status_bar()

        if MouseState().button1.dragging:

            if self.user_dragging:
                self.on_drag(arg['AltDown'], arg['ShiftDown'])
                self.view.redraw()

            else:
                self.start_drag()
                self.user_dragging = True

    def button_event(self, arg):
        """
        Override base button actions
        """

        if MouseState().button1.state == 'UP':

            #terminate dragging if button is released
            if self.user_dragging and not MouseState().button1.dragging:
                self.end_drag()
                self.user_dragging = False

            return

        if not MouseState().component:
            return

        _idx = int(MouseState().component.split('-')[1])

        for _i, _v in enumerate(self.trackers['Nodes']):

            _v.state.selected.value = _i >= _idx

            if _i == _idx and not MouseState().ctrlDown:
                break

            _v.state.selected.ignore = True

        if _idx > 0:
            _idx -= 1

        for _i, _v in enumerate(self.trackers['Tangents']):

            _v.state.selected.value = _i >= _idx

            if _i == _idx and not MouseState().ctrlDown:
                break

            _v.state.selected.ignore = True

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

            _tr = NodeTracker(
                view=self.view,
                names=_names + ['NODE-' + str(_i)],
                point=_pt
            )

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
                    points=[_v.get() for _v in _nodes]
                )
            )

        _curves = self.alignment.get_curves()
        _points = []

        self.trackers = _result

        return

        #curve trackers
        for _i in range(0, len(_result['Tangents']) - 1):

            _ct = CurveTracker(
                view=self.view,
                names=_names + ['CURVE-' + str(_i)],
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

        _wt = WireTracker(view=self.view, names=wire_name)

        _wt.set_selectability(select)
        _wt.set_selection_nodes(nodes)
        _wt.update(points)

        return _wt

    def start_drag(self):
        """
        Set up the scene graph for dragging operations
        """

        #set the drag start point to the first selected node
        for _i, _v in enumerate(self.trackers['Nodes']):

            if not _v.state.selected.value:
                continue

            _c = _v.get()

            #drag start may exist if the user has switched between
            #translation and rotation
            if not self.drag.start:

                self.drag.start = _c
                self.drag.position = _c
                self.drag.center = _c
                self.drag.object = _v

                _v.state.selected.value = True
                _v.state.selected.ignore = True

            if self.drag.nodes:

                if self.drag.nodes[-1] == _c:
                    continue

            self.drag.nodes.append(_c)
            self.drag.node_idx.append(_i)

        #temporarily disable geometry selectability
        #self.set_selectability(False)

        #self.curves = self.alignment.get_curves()
        self.pi_list = self.alignment.model.get_pi_coords()

        _partial = []
        #_curves = []

        #save the current tracker state before editing for
        #restoration if drag ops yield invalid alignment
        self.drag.tracker_state = [Vector(_v) for _v in self.drag.nodes]

        #duplicate scene nodes of selected and partially-selected wires
        for _i, _v in enumerate(self.trackers['Tangents']):

            _state = [_x.state.selected.value for _x in _v.selection_nodes]

            if not any(_state):
                continue

            _g = 'SELECTED'

            if not all(_state):

                _g = 'PARTIAL'
                _partial.append(_i)
                _v.state.selected.value = self.State.SELECT_PARTIAL

                #if _i > 0 and not _i - 1 in _curves:
                #    _curves.append(_i - 1)

                #if _i < len(self.curves):
                #    _curves.append(_i)

            self.groups[_g].addChild(_v.copy())

        self.drag.multi = self.groups['SELECTED'].getNumChildren() > 2

        #for _i in _curves:
        #    self.trackers['Curves'][_i].selected = True

        #for _v in self.trackers['Curves']:
            #_v.update_selection_state()

        #self.drag.curves = _curves

    def on_drag(self, do_rotation, modify):
        """
        Update method during drag operations
        """

        if self.drag.start is None:
            return

        _world_pos = MouseState().coordinates.sub(self.datum)

        self._update_transform(_world_pos, do_rotation, modify)
        self._update_pi_nodes(_world_pos)

        #for _curve in self.trackers['Curves']:
        #    _curve.update()

        #self._validate_alignment()

        self.drag.position = _world_pos

    def end_drag(self):
        """
        Cleanup method for drag operations
        """

        if self.is_valid:

            print('valid')
            _pi_list = [Vector(_v.point) for _v in self.trackers['Nodes']]
            #self.datum = _pi_list[0]
            self.transform.translation.setValue(tuple(self.datum))

        else:

            print('invalid')
            for _v in self.trackers['Curves']:
                _v.update()
                _v.state.selected.ignore = False

        #write the original node positions back to node trackers, if valid
        for _i, _v in enumerate(self.trackers['Nodes']):

            _pt = None

            if not self.is_valid:
                _pt = self.drag.tracker_state[_i]

            _v.update(_pt)
            _v.state.selected.ignore = False

        for _v in self.trackers['Tangents']:
            _v.update()
            _v.state.selected.ignore = False

        self.set_selectability(True)

        self.drag.object.state.selected.ignore = False
        self.drag.reset()

        self.drag_transform.center = coin.SbVec3f((0.0, 0.0, 0.0))
        self.drag_transform.translation.setValue((0.0, 0.0, 0.0))
        self.drag_transform.rotation = coin.SbRotation()

        #remove child nodes from the selected group
        self.groups['SELECTED'].removeAllChildren()
        self.groups['SELECTED'].addChild(self.drag_transform)
        self.groups['SELECTED'].addChild(coin.SoSeparator())

        #remove child nodes from the partial group
        self.groups['PARTIAL'].removeAllChildren()

    def set_selectability(self, is_selectable):
        """
        Override of the base implementation
        """

        for _v in self.trackers['Nodes'] + self.trackers['Curves']:

            _v.set_selectability(is_selectable)

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
        _search.apply(self.view.getSceneGraph())

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(self.viewport)
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

    def _validate_alignment(self):
        """
        Given a list of updated curves, validate them against themselves
        and adjoining geometry
        """

        if not self.drag.curves:
            self.is_valid = True
            return

        _idx = self.drag.curves[:]
        curves = [self.trackers['Curves'][_v].curve for _v in self.drag.curves]

        #append preceding and following curves if first / last curves
        #aren't being updated
        if _idx[0] > 0:
            _idx.insert(0, _idx[0] - 1)
            curves.insert(0, self.curves[_idx[0]])

        elif _idx[-1] < len(self.curves) - 1:
            _idx.append(_idx[-1] + 1)
            curves.append(self.curves[_idx[-1]])

        _styles = [CoinStyle.DEFAULT]*len(curves)

        #validate curves against each other,
        #ensuring PI distance >= sum  of curve tangents
        for _i in range(0, len(curves) - 1):

            _tangents = []
            _pair = [curves[_i], curves[_i + 1]]

            for _c in _pair:

                if _c['Type'] == 'Spiral':

                    _tangents.append(spiral.get_ordered_tangents(_c)[0])
                    continue

                _tangents.append(_c['Tangent'])

            if (_tangents[0] + _tangents[1])\
                > (_pair[0]['PI'].distanceToPoint(_pair[1]['PI'])):

                _styles[_i + 1] = CoinStyle.ERROR
                _styles[_i] = CoinStyle.ERROR

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
            if _c['Type'] == 'Spiral':

                _tans = spiral.get_ordered_tangents(_c)
                _tangent = _tans[1]

                if _i == 0:
                    _tangent = _tans[0]

            else:
                _tangent = _c['Tangent']

            if _styles[_i] != CoinStyle.ERROR \
                and _tangent > _c['PI'].distanceToPoint(_p):

                _styles[_i] = CoinStyle.ERROR

        for _i, _c in enumerate(curves):
            self.trackers['Curves'][_idx[0] + _i].set_style(
                _styles[_i]
            )

        self.is_valid = all([_v != CoinStyle.ERROR for _v in _styles])

    def finalize(self):
        """
        Cleanup the tracker
        """

        for _t in self.trackers.values():

            for _u in _t:
                print(_u.names)
                _u.finalize()

        self.remove_node(self.groups['EDIT'], self.node)
        self.remove_node(self.groups['DRAG'], self.node)

        if self.callbacks:
            for _k, _v in self.callbacks.items():
                self.view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        print('finalizing alignment tracker...')
        super().finalize()
