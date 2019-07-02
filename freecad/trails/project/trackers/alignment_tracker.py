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
        self.pi_list = []

        self.drag = {
            'Start': Vector(),
            'Multi': False,
            'PI': [],
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
                self.start_drag_2()
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

    def start_drag_2(self):
        """
        Set up the scene graph for dragging operations
        """

        self.drag['Start'] = self.view.getPoint(self.mouse.pos)
        self.curves = self.alignment.get_curves()
        self.pi_list = self.alignment.model.get_pi_coords()
        self.drag['PI'] = self.pi_list[:]

        _partial = []

        #duplciate scene nodes of selected and partially-selected wires
        for _v in self.trackers['Tangents'] + self.trackers['Curves']:

            if _v.state == 'UNSELECTED':
                continue

            self.groups[_v.state].addChild(_v.copy())

        self.drag['Multi'] = self.groups['SELECTED'].getNumChildren() > 1

        #get paritally selected tangents to build curve index
        _partial = [
            _i for _i, _v in enumerate(self.trackers['Tangents'])\
                if _v.state == 'PARTIAL'
        ]

        _curves = []

        #build list of curve indices
        for _i in _partial:

            if _i > 0 and not(_i - 1) in _curves:
                _curves.append(_i - 1)

            if _i < len(self.curves):
                _curves.append(_i)

        self.drag['Curves'] = _curves

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

        print([_v for _v in self.drag['PI']])

        if self.is_valid:

            self.alignment.update_curves(self.curves, self.drag['PI'])

            for _i, _v in enumerate(self.alignment.model.get_pi_coords()):
                print(_v)
                self.trackers['Nodes'][_i].update(_v)

            for _v in self.trackers['Tangents']:
                _v.update([_w.get() for _w in _v.selection_nodes])

        #clear the drag_geometry dict
        for _v in self.drag.values():

            if isinstance(_v, Vector):
                _v = Vector()

            elif isinstance(_v, bool):
                _v = False

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

        _pos = tuple(pos.sub(self.drag['Start']))

        self.drag_transform.translation.setValue(_pos)

    def _update_pi_nodes(self, world_pos):
        """
        Internal function - Update wires for partially-selected tangents
        """

        _curves = self.drag['Curves']
        _k = 0

        for _i in range(_curves[0], _curves[-1] + 2):

            _v = self.trackers['Tangents'][_i]

            if _v.state != 'PARTIAL':
                continue

            _pts = []

            for _j, _w in enumerate(_v.selection_nodes):

                _p = _w.get()

                if _w.state == 'SELECTED':

                    _p = tuple(
                        self.pi_list[_i + _j].add(
                            world_pos.sub(self.drag['Start'])
                        )
                    )

                    self.drag['PI'][_i + _j] = Vector(_p)

                _pts.append(_p)

            self.groups['PARTIAL'][_k].getChild(4).point.setValues(_pts)

            _k += 1

    def _transform_nodes(self, nodes):
        """
        Transform selected nodes by the transformation matrix
        """

        _matrix = self.get_matrix()
        _result = []
        _world = self.view.getPoint(self.mouse.pos)

        for _n in nodes:

            _v = _n

            if _matrix is not None:

                _v = coin.SbVec4f(tuple(_n) + (1.0,))
                _v = _matrix.multVecMatrix(_v).getValue()[:3]

            else:
                _v = _v.add(_world.sub(self.drag['Start']))

            _result.append(Vector(_v))

        return _result

    def _generate_curves(self):
        """
        _Internal function - Generate curves based on existing curves and nodes
        """

        #get the indices of curves that are to be updated
        _indices = self.drag['Curves']

        _result = []
        _rng = (_indices[0], _indices[-1] + 3)
        _nodes = self.pi_list[_rng[0]:_rng[1]]

        for _i, _v in enumerate(self.trackers['Nodes'][_rng[0]:_rng[1]]):

            if _v.state == 'SELECTED':
                _nodes[_i] = self._transform_nodes([_v.get()])[0]

        _j = 0

        for _i in _indices:

            _start = _nodes[_j]
            _pi = _nodes[_j + 1]
            _end = _nodes[_j + 2]

            _curve = arc.get_parameters(
                {
                    'BearingIn': support.get_bearing(_pi.sub(_start)),
                    'BearingOut': support.get_bearing(_end.sub(_pi)),
                    'PI': _pi,
                    'Radius': self.curves[_i]['Radius'],
                }
            )

            _points, _x = arc.get_points(_curve)

            #save a reference to the tracker for later validation and update
            #_curve['tracker'] = self.trackers['Curves'][_idx]
            #_curve['tracker'].update(_points)

            self.curves[_i] = _curve

            _result.append(_curve)

            self.trackers['Curves'][_i].update(_points)

            _j += 1

        return _result

    def _validate_curves(self, curves):
        """
        Given a list of updated curves, validate them against themselves
        and adjoingin geometry
        """

        _idx = self.drag['Curves']

        #append preceeding and following curves if first / last curves
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

            _c = [curves[_i], curves[_i + 1]]

            if (_c[0]['Tangent'] + _c[1]['Tangent'])\
                > (_c[0]['PI'].distanceToPoint(_c[1]['PI'])):

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
            _p = self.drag['PI'][_i]

            if _styles[_i] != CoinStyle.ERROR:

                if _c['Tangent'] > _c['PI'].distanceToPoint(_p):
                    _styles[_i] = CoinStyle.ERROR

        for _i, _c in enumerate(curves):
            self.trackers['Curves'][_idx[0] + _i].set_style(
                _styles[_i]
            )

        self.is_valid = all([_v != CoinStyle.ERROR for _v in _styles])
