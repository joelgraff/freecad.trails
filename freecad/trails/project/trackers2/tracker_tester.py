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

from FreeCAD import Vector

import FreeCADGui as Gui

#from ..support.publisher import PublisherEvents as Events

from .marker_tracker import MarkerTracker
from .line_tracker import LineTracker
from .trait.base import Base
from .trait.event import Event
from .trait.select import Select

class TrackerTester(Base, Event, Select):
    """
    Tracker class for alignment design
    """

    def __init__(self, doc, object_name, alignment, is_linked, parent,
                 datum=Vector()):
        """
        Constructor
        """

        super().__init__(
            name='.'.join([doc.Name, object_name, 'TRACKER_TESTER']),
            parent=parent
        )

        self.alignment = alignment
        self.doc = doc
        self.user_dragging = False
        self.status_bar = Gui.getMainWindow().statusBar()
        self.pi_list = []
        self.datum = alignment.model.data['meta']['Start']

        #don't handle events, as this is a global-level tracker
        self.handle_events = False

        #base (placement) transformation for the alignment
        self.transform.translation.setValue(
            tuple(alignment.model.data['meta']['Start'])
        )

        #generate initial node trackers and wire trackers for mouse interaction
        #and add them to the scenegraph
        self.trackers = None
        self.build_trackers(is_linked)

        _trackers = []

        for _v in self.trackers.values():
            _trackers.extend(_v)

        for _v in _trackers:
            self.insert_group(_v)

        #selection state for de-selection / unhighlighting
        self.add_mouse_event(self.select_mouse_event)
        self.add_button_event(self.select_button_event)

        #self.add_mouse_event(self.mouse_event)
        self.set_visibility(True)

    def _update_status_bar(self):
        """
        Update the status bar with the latest mouseover data
        """

        #self.status_bar.showMessage(
        #   MouseState().component + ' ' + str(tuple(MouseState().coordinates))
        #)

        pass

    def post_select_event(self, arg):
        """
        Event to force wires to re-test selection state on button down
        """

        pass
        #if MouseState().button1.state == 'UP':
        #    return

        #for _v in self.trackers['Tangents']:
        #    _v.validate_selection()

    def build_trackers(self, is_linked):
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
        _result = {'Nodes': [], 'Tangents': [], 'Curves': []}

        #node trackers
        for _i, _pt in enumerate(_nodes):

            _v = MarkerTracker(
                name='.'.join(self.names[0:2] + ['MARKER-'+str(_i)]),
                point=_pt,
                parent=self.base
            )

            _result['Nodes'].append(_v)

        _result['Nodes'][0].is_end_node = True
        _result['Nodes'][-1].is_end_node = True

        #line trackers - Tangents
        for _i in range(0, len(_result['Nodes']) - 1):

            _nodes = _result['Nodes'][_i:_i + 2]
            _points = [_v.point for _v in _nodes]

            if is_linked:
                _points = None
            else:
                _nodes = None

            _result['Tangents'].append(
                LineTracker(
                    name='.'.join(self.names[0:2] + ['LINE'+str(_i)]), 
                    points=_points,
                    parent=self.base
                )
            )

        #        self._build_wire_tracker(
        #            wire_name=_names + ['WIRE-' + str(_i)],
        #            nodes=_nodes,
        #            points=_points,
        #            select=True
        #        )
        #    )

        self.trackers = _result

    def _build_wire_tracker(self, wire_name, nodes, points, select=False):
        """
        Convenience function for WireTracker construction
        """

        pass
        #_wt = WireTracker(names=wire_name)

        #_wt.set_selectability(select)
        #_wt.set_points(points, nodes)
        #_wt.update()

        #if nodes:
        #    for _n in nodes:
        #        _n.register(_wt, Events.NODE.EVENTS)

        #return _wt

    def finalize(self, node=None, parent=None):
        """
        Cleanup the tracker
        """

        for _t in self.trackers.values():

            for _u in _t:
                _u.finalize()

        super().finalize(node, parent)
