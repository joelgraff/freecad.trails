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
Customized wire tracker from DraftTrackers.wireTracker
"""

from enum import IntEnum

from pivy import coin

import FreeCADGui as Gui
from FreeCAD import Vector

from DraftGui import todo

from ..containers import TrackerContainer

from ..support.mouse_state import MouseState
from ..support.view_state import ViewState
from ..support.drag_state import DragState

from .coin_style import CoinStyle

class BaseTracker:
    """
    A custom base Draft Tracker
    """

    class State(IntEnum):
        """
        State enum class for base tracker state values
        """
        UNDEFINED = 0

        ENABLE_OFF = 1
        ENABLE_ON = 2

        VISIBLE_OFF = 1
        VISIBLE_ON = 2

        SELECT_OFF = 1
        SELECT_ON = 2
        SELECT_PARTIAL = 4

    def __init__(self, names, children=None, has_events=True):
        """
        Constructor
        """

        self.names = names
        self.name = names[2]
        self.state = TrackerContainer()

        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()
        self.node = coin.SoSeparator()
        self.parent = None
        self.picker = coin.SoPickStyle()
        self.switch = coin.SoSwitch()
        self.coin_style = CoinStyle.DEFAULT
        self.active_style = None
        self.conditions = []

        if not children:
            children = []

        #if group:
        #    self.node = coin.SoGroup()

        self.sel_node = \
            coin.SoType.fromName("SoFCSelection").createInstance()

        self.sel_node.documentName.setValue(names[0])
        self.sel_node.objectName.setValue(names[1])
        self.sel_node.subElementName.setValue(names[2])

        for child in [
                self.picker, self.draw_style, self.color
            ] + children:

            self.node.addChild(child)

        _sep = coin.SoSeparator()

        _sep.addChild(self.sel_node)
        _sep.addChild(self.node)

        self.switch.addChild(_sep)
        self.callbacks = None

        if has_events:

            self.callbacks = {
                'SoLocation2Event':
                    ViewState().view.addEventCallback(
                        'SoLocation2Event', self.mouse_event),

                'SoMouseButtonEvent':
                    ViewState().view.addEventCallback(
                        'SoMouseButtonEvent', self.button_event)
            }

        #bypass overrides on intialization
        BaseTracker.set_style(self, CoinStyle.DEFAULT)
        BaseTracker.set_visible(self, True)

    def refresh(self, style=None, visible=None):
        """
        Upate the tracker to reflect state changes
        """

        if not style:
            style = self.active_style

        self._process_conditions()

        self.set_style(style)
        self.set_visible(visible)

    def mouse_event(self, arg):
        """
        SoLocation2Event callback
        """

        #pre-empptive abort conditions
        if not self.state.enabled.value:
            return

        if not self.state.visible.value:
            return

        #abort if dragging to avoid highlighting tests
        self.update_dragging()

        if self.state.dragging:
            return

        if self.state.selected.value:
            return

        self.update_highlighting()

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        #ignore mouse up unless this not a multi-select click
        #and the node was not previously multi-selected
        #allows for node selction state to remain if user multi-selects
        #the node, then clicks on a different node to begin drag operations

        _persist_multi_select = \
            not MouseState().ctrlDown and self.state.was_multi_selected

        if MouseState().button1.state == 'UP':

            if not _persist_multi_select or self.state.was_dragged:
                return

        elif _persist_multi_select:
            return

        #preemptive abort conditions
        if not self.state.enabled.value:
            return

        if not self.state.visible.value:
            return

        _multi_select = MouseState().ctrlDown and self.state.multi_select

        #selection logic - skip once if ignore flag is set
        if not self.state.selected.ignore:

            if self.name == MouseState().component:

                if MouseState().ctrlDown and self.state.selected.value:
                    self.state.selected.value = False

                else:
                    self.state.selected.value = True

            #deselect unless multi-selecting or at the end of a drag op
            elif (self.state.selected.value and not _multi_select) \
                and not self.state.dragging:

                self.state.selected.value = False

        _style = self.coin_style

        if self.state.selected.value:
            _style = CoinStyle.SELECTED

        self.refresh(_style)

        _end_of_drag = _persist_multi_select and self.state.was_dragged

        if MouseState().button1.pressed and not _persist_multi_select:
            self.state.was_multi_selected = MouseState().ctrlDown

    def update_highlighting(self):
        """
        Test for highlight conditions and changes
        """

        _style = None

        #highlight logic - skip if ignore flag is set
        if not self.state.selected.ignore:

            _style = self.coin_style

            #test to see if this node is under the cursor
            self.state.highlighted = self.name == MouseState().component

            if self.state.highlighted:
                _style = CoinStyle.SELECTED

        self.refresh(_style)

    def update_dragging(self):
        """
        Test for drag conditions and changes
        """

        if MouseState().button1.dragging and self.state.selected.value:

            if not self.state.dragging:

                self.start_drag()
                self.state.dragging = True

            else:
                self.on_drag()

        elif self.state.dragging:

            self.end_drag()
            self.state.dragging = False

    def start_drag(self):
        """
        Initialize drag ops
        """

        DragState().add_node(self.copy())

        if not DragState().node:

            DragState().node = self
            DragState().start = MouseState().coordinates
            self.insert_node(DragState().group, 0)

    def on_drag(self):
        """
        Ongoing drag ops
        """

        if self == DragState().node:

            DragState().transform.translation.setValue(
                tuple(MouseState().coordinates.sub(DragState().start))
            )

    def end_drag(self):
        """
        Terminate drag ops
        """

        DragState().finish()
        self.state.dragging = False

    def set_selectability(self, is_selectable):
        """
        Set the selectability of the node using the SoPickStyle node
        """

        _state = coin.SoPickStyle.UNPICKABLE

        if is_selectable:
            _state = coin.SoPickStyle.SHAPE

        self.picker.style.setValue(_state)

    def is_selectable(self):
        """
        Return a bool indicating whether or not the node may be selected
        """

        return self.picker.style.getValue() != coin.SoPickStyle.UNPICKABLE

    def set_visible(self, visible=None):
        """
        Update the tracker visibility
        """

        if self.state.visible.ignore:
            return

        if visible is None:
            visible = self.state.visible.value

        if visible:
            self.switch.whichChild = 0
        else:
            self.switch.whichChild = -1

        self.state.visible.value = visible

    def set_base_style(self, style=None):
        """
        Set the base style of the tracker
        """

        if style is None:
            style = CoinStyle.DEFAULT

        self.coin_style = style

    def set_style(self, style=None):
        """
        Update the tracker style
        """

        if not style:
            style = self.coin_style

        if self.active_style == style:
            return

        if style['line width']:
            self.draw_style.lineWidth = style['line width']

        self.draw_style.style = style['line style']

        self.draw_style.lineWeight = style['line weight']

        if style['line pattern']:
            self.draw_style.linePattern = style['line pattern']

        if hasattr(self, 'marker'):
            self.marker.markerIndex = \
                Gui.getMarkerIndex(style['shape'], style['size'])

        if style.get('color'):
            self.color.rgb = style['color']

        self.active_style = style

    def finalize(self, node=None, parent=None):
        """
        Node destruction / cleanup
        """

        if node is None:
            node = self.node

        self.remove_node(node, parent)

    def copy(self, node=None):
        """
        Return a copy of the tracker node
        """

        if not node:
            node = self.node

        return node.copy()

    def _process_conditions(self):
        """
        Process the conditions which determine node visiblity
        """

        if not self.conditions:
            return

        _c = MouseState().component

        if not _c:
            return

        for _cond in self.conditions:

            if (_cond[0] == '!' and _cond[1:] not in _c) or (_cond in _c):

                self.set_visible(False)
                break

    def transform_nodes(self, nodes):
        """
        Transform selected nodes by the transformation matrix
        """

        _result = []

        if not DragState().matrix:
            return _result

        for _n in nodes:

            _v = coin.SbVec4f(tuple(_n) + (1.0,))
            _v = DragState().matrix.multVecMatrix(_v).getValue()[:3]

            _result.append(Vector(_v)) #.sub(self.datum))

        return _result

    def insert_node(self, node, parent=None):
        """
        Insert a node as a child of the passed node
        """

        _fn = lambda _x: ViewState().sg_root.insertChild(_x, 0)

        if parent:
            _fn = parent.addChild

        todo.delay(_fn, node)

    def remove_node(self, node, parent=None):
        """
        Convenience wrapper for _remove_node
        """

        if not parent:
            parent = ViewState().sg_root

        if parent.findChild(node) >= 0:
            todo.delay(parent.removeChild, node)
