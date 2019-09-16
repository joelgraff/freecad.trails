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

from .base_tracker import BaseTracker

from ..support.mouse_state import MouseState
from ..support.view_state import ViewState
from ..support.select_state import SelectState
from ..support.drag_state import DragState
from ..support.publisher import Publisher
from ..support.publisher import PublisherEvents as Events

from .node_tracker import NodeTracker
from .wire_tracker import WireTracker
from .curve_tracker import CurveTracker

class AlignmentTracker(BaseTracker, Publisher):
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
        self.datum = alignment.model.data.get('meta').get('Start')
        self.drag_curves = []

        self.message_queue = {}

        #base (placement) transformation for the alignment
        self.transform = coin.SoTransform()
        self.transform.translation.setValue(
            tuple(alignment.model.data.get('meta').get('Start'))
        )
        super().__init__(names=self.names, children=[self.transform])

        #scenegraph node structure for editing and dragging operations
        self.groups = {
            'EDIT': coin.SoGroup(),
            'DRAG': coin.SoGroup(),
            'SELECTED': coin.SoSeparator(),
            'PARTIAL': coin.SoSeparator(),
        }

        self.state.draggable = True

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
            self.insert_node(_v.get_node(), self.groups['EDIT'])

        #insert in the scenegraph root
        self.insert_node(self.get_node())

        self.select_cb = \
            ViewState().view.addEventCallback(
                'SoMouseButtonEvent', self.post_select_event)

    def notify(self, event_type, message):
        """
        Override subscriber base implementation
        """

        #during dragging operations, sink all notifications here.
        #at the end of drag ops, pass on update to panel
        #if multiple nodes were selected, compute transformation
        #and pass on to panel

        #super().notify(event_type, message, True)

        #if event_type != Events.TASK.EVENTS:
        #    self.dispatch(Events.ALIGNMENT.EVENTS, message, True)
        #    return

        self.dispatch(Events.ALIGNMENT.UPDATED, message, False)

    def get_updates(self):
        """
        Return latest geometry updates in message queue
        """

        _queue_len = len(self.message_queue)

        if not _queue_len:
            return {}

        _result = []

        for _v in self.message_queue.values():
            _result.append(
                {
                    'position': _v['position'],
                    'translation': _v['translation'].getValue(),
                    'rotation': _v['rotation'].getValue()
                }
            )

        return _result

    def _update_status_bar(self):
        """
        Update the status bar with the latest mouseover data
        """

        self.status_bar.showMessage(
            MouseState().component + ' ' + str(tuple(MouseState().coordinates))
        )

    def on_drag(self):
        """
        Override base function
        """

        #iterate curves to find curves being dragged
        self.drag_curves = [
            _v for _v in self.trackers['Curves'] if _v.state.dragging
        ]

        _last_tan = 0.0

        for _i, _v in enumerate(self.drag_curves):

            _next_tan = 0.0

            if _i < len(self.drag_curves) - 1:

                _dc = self.drag_curves[_i + 1]

                if _dc.drag_curve:
                    _next_tan = _dc.drag_curve.get('Tangent')

            _v.validate(_last_tan, _next_tan)
            _last_tan = _v.drag_curve.get('Tangent')

    def end_drag(self):
        """
        Override base fucntion
        """

        super().end_drag()

        for _v in self.drag_curves:

            if not _v.is_valid:
                DragState().abort = True

        self.drag_curves = []

    def post_select_event(self, arg):
        """
        Event to force wires to re-test selection state on button down
        """

        if MouseState().button1.state == 'UP':
            return

        for _v in self.trackers['Tangents']:
            _v.validate_selection()

    def button_event(self, arg):
        """
        Override base button actions
        """

        # dispatch an empty message if nothing is selected
        # abort if not multi-selecting or button up
        if MouseState().button1.state == 'UP':

            _sel = [_v.is_selected() for _v in self.trackers['Curves']]

            if not any(_sel):
                self.notify(Events.ALIGNMENT.EVENTS, [None, None])

            super().button_event(arg)
            return

        _pick = MouseState().component

        for _v in self.trackers['Nodes']:

            if not _v.is_visible():
                _v.set_visibility(True)

        #node selection is multi-select only
        if 'NODE' in _pick and MouseState().ctrlDown:

            #get the nodes we need to select, and select them
            _idx = int(_pick.split('-')[1]) + 1

            for _v in self.trackers['Nodes'][_idx:]:
                SelectState().select(_v, force=True)

    def build_trackers(self):
        """
        Build the node and wire trackers that represent the selectable
        portions of the alignment geometry
        """

        _model = self.alignment.model.data

        #build a list of coordinates from curves in the geometry
        _nodes = [Vector()]
        _nodes += [_v.get('PI')\
            for _v in _model.get('geometry') if _v.get('Type') != 'Line']

        _nodes += [_model.get('meta').get('End')]

        #build the trackers
        _names = self.names[:2]
        _result = {'Nodes': [], 'Tangents': [], 'Curves': []}

        #node trackers
        for _i, _pt in enumerate(_nodes):

            _tr = NodeTracker(names=_names + ['NODE-' + str(_i)], point=_pt)

            #register the node as a subscriber to aligntment NODE_EVENT
            #self.register(_tr, Events.ALIGNMENT.EVENTS)

            #register the alignment as a sUbscriber to node NODE_EVENT
            _tr.register(self, [Events.NODE.POSITION, Events.NODE.SELECTED])

            _result['Nodes'].append(_tr)

        _result['Nodes'][0].is_end_node = True
        _result['Nodes'][-1].is_end_node = True

        #wire trackers - Tangents
        for _i in range(0, len(_result['Nodes']) - 1):

            _nodes = _result['Nodes'][_i:_i + 2]

            _wt = WireTracker(names=_names + ['WIRE-' + str(_i)])

            #NECESSARY??
            #self.register(_wt, Events.WIRE_EVENT)
            #_wt.register(self, Events.WIRE_EVENT)

            _wt.set_selectability(False)
            _wt.set_points(nodes=_nodes)
            _wt.update()

            _result['Tangents'].append(_wt)

        #curve trackers
        _curves = self.alignment.get_curves()

        for _i in range(0, len(_result['Tangents']) - 1):

            _ct = CurveTracker(
                names=_names[:2] + ['CURVE-' + str(_i)],
                curve=_curves[_i],
                pi_nodes=_result['Nodes'][_i:_i+3]
            )

            _ct.set_selectability(True)

            #self.register(_ct, Events.CURVE_EVENTS)
            #_ct.register(self, Events.CURVE.EVENTS)
            _ct.register(self, Events.CURVE.EVENTS)

            _result['Curves'].append(_ct)

        self.trackers = _result

    def finalize(self):
        """
        Cleanup the tracker
        """

        for _t in self.trackers.values():
            for _u in _t:
                _u.finalize()

        self.remove_node(self.groups['EDIT'], self.get_node())
        self.remove_node(self.groups['DRAG'], self.get_node())

        if self.callbacks:
            for _k, _v in self.callbacks.items():
                ViewState().view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        super().finalize()
