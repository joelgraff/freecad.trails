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

        self.view = view
        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        #generate inital node trackers and wire trackers for mouse interaction
        self.build_trackers()

        super().__init__(names=self.names, select=False, group=True)

        #add the tracker geometry to the scenegraph
        for _v in self.trackers['Nodes'] + self.trackers['Wires']:
            self.insert_node(_v.node, self.node)

        #insert in the scenegraph root
        self.insert_node(self.node)

        #self.setup_callbacks()

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
        _result = {'Nodes': [], 'Wires': []}

        #node trackers
        for _i, _pt in enumerate(_nodes):

            _tr = NodeTracker(
                view=self.view, names=_names + ['NODE-' + str(_i)], point=_pt
            )
            _tr.update(_pt)

            _result['Nodes'].append(_tr)

        #wire trackers
        for _i in range(0, len(_result['Nodes']) - 1):

            _points = _result['Nodes'][_i:_i + 2]

            _result['Wires'].append(WireTracker(
                names=_names + ['WIRE-' + str(_i - 1)], points=_points
            ))

        self.trackers = _result

    def setup_callbacks(self):
        """
        Setup event handling callbacks and return as a list
        """

        #self.callbacks['SoKeybaordEvent'] = \
        #    self.view.addEventCallback('SoKeyboardEvent', self.key_action)

        self.callbacks['SoLocation2Event'] = \
            self.view.addEventCallback('SoLocation2Event', self.mouse_action)

        self.callbacks['SoMouseButtonEvent'] = \
            self.view.addEventCallback(
                'SoMouseButtonEvent', self.button_action)