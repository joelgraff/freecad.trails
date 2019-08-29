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
from ..support.select_state import SelectState

from .coin_styles import CoinStyles

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

        self.node_ok = False
        self.names = names
        self.name = names[2]
        self.state = TrackerContainer()

        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()
        self.node = coin.SoSeparator()
        self.parent = None
        self.picker = coin.SoPickStyle()
        self.switch = coin.SoSwitch()

        self.coin_style = CoinStyles.DEFAULT
        self.active_style = None

        self.matrix = None

        self.drag_group = None
        self.drag_copy = None

        self.select_state = ''

        self.show_drag_line = True

        self.partial_idx = []   #list to store indices for partial selections
        self.do_unset = False

        if not children:
            children = []

        self.sel_node = \
            coin.SoType.fromName("SoFCSelection").createInstance()

        self.sel_node.documentName.setValue(names[0])
        self.sel_node.objectName.setValue(names[1])
        self.sel_node.subElementName.setValue(names[2])

        for child in [
                self.picker, self.draw_style, self.color
            ] + children:

            self.node.addChild(child)

        self.separator = coin.SoSeparator()

        self.separator.addChild(self.sel_node)
        self.separator.addChild(self.node)

        self.switch.addChild(self.separator)
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

        #bypass overrides on initialization
        BaseTracker.set_style(self, CoinStyles.DEFAULT)
        BaseTracker.set_visibility(self, True)

        self.switch.whichChild = 0

    def is_selected(self):
        """
        Convenience wrapper for SelectState().is_selceted
        """

        return SelectState().is_selected(self) != ''

    def get_node(self):
        """
        Return the root scenegraph node for the base tracker.
        Provided for overriding to allow for different node structures
        """

        return self.separator

    def refresh(self, style=None, visible=None):
        """
        Update the tracker to reflect state changes
        """

        if not style:

            style = self.coin_style

            if self.is_selected():
                style = CoinStyles.SELECTED

        #self._process_conditions()
        self.set_style(style)

        if visible is not None:
            self.set_visibility(visible)

    def mouse_event(self, arg):
        """
        SoLocation2Event callback
        """

        #pre-emptive abort conditions
        if not self.state.enabled.value:
            return

        if not self.is_visible():
            self.refresh()

        self.update_dragging()
        self.update_highlighting()

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        #preemptive abort if not both enabled and visible
        if not (self.state.enabled.value and self.is_visible()):
            return

        if MouseState().button1.state == 'DOWN':
            SelectState().select(self)

        self.refresh()

    def update_highlighting(self):
        """
        Test for highlight conditions and changes
        """

        if self.state.dragging or not self.is_visible() or self.is_selected():
            return

        #highlight logic - skip if ignore flag is set
        #if not self.state.selected.ignore:

        _style = self.coin_style

        #test to see if this node is under the cursor
        self.state.highlighted = self.name == MouseState().component

        if self.state.highlighted:
            _style = CoinStyles.SELECTED

        self.refresh(_style)

    def update_dragging(self):
        """
        Test for drag conditions and changes
        """

        #all draggable objects get drag events
        if not self.state.draggable:
            return

        #if mouse is dragging, then start / on drag are viable events
        if MouseState().button1.dragging:

            if not self.state.dragging:
                self.before_drag()
                self.start_drag()

            else:
                self.on_drag()

        #otherwise, end_drag is the only option
        elif self.state.dragging:

            self.end_drag()
            self.state.dragging = False

    def before_drag(self):
        """
        Default implementation
        """

        pass

    def start_drag(self):
        """
        Initialize drag ops
        """

        #copy the tracker node structure to the drag state node for
        #transformations during drag operations

        self.select_state = SelectState().is_selected(self)

        self.drag_copy = self.copy()
        self.drag_group = None

        if self.select_state == 'FULL':
            self.drag_group = DragState().add_node(self.drag_copy)

        elif self.select_state == 'PARTIAL':

            if self.partial_idx:
                self.drag_group = \
                    DragState().add_partial_node(
                        self.drag_copy, self.partial_idx)

        elif self.select_state == 'MANUAL':
            self.drag_group = DragState().add_manual_node(self.drag_copy)

        else:
            self.drag_copy = None

        self.state.dragging = True

        if self.name == MouseState().component:

            DragState().drag_node = self
            DragState().start = MouseState().coordinates
            DragState().coordinates = MouseState().coordinates
            DragState().insert()

    def on_drag(self):
        """
        Ongoing drag ops
        """

        #tracker must be picked for dragging and actively dragged.
        #Prevents multiple updates in the same mose movement

        if not self.state.dragging or self != DragState().drag_node:
            return

        _drag_line_start = DragState().start
        _drag_line_end = MouseState().coordinates
        _mouse_coord = MouseState().coordinates

        #drag rotation
        if MouseState().altDown:

            DragState().rotate(_mouse_coord)

            _ctr = Vector(DragState().transform.center.getValue())
            _offset = Vector(DragState().transform.translation.getValue())

            _drag_line_start = _ctr.add(_offset)

            _mouse_coord = DragState().coordinates

        #drag translation
        else:
            DragState().translate(_mouse_coord)

        #save the drag state coordinate as the current mouse coordinate
        DragState().coordinates = _mouse_coord

        if self.show_drag_line:
            DragState().update(_drag_line_start, _drag_line_end)

    def end_drag(self):
        """
        Terminate drag ops
        """

        if not self.state.dragging:
            return

        self.drag_copy = None
        self.select_state = ''

        DragState().finish()

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

    def set_visibility(self, visible=True):
        """
        Update the tracker visibility
        """

        if visible:
            self.switch.whichChild.setValue(0)

        else:
            self.switch.whichChild.setValue(-1)

    def is_visible(self):
        """
        Return the visibility of the tracker
        """

        return self.switch.whichChild.getValue() == 0

    def set_base_style(self, style=None):
        """
        Set the base style of the tracker
        """

        if style is None:
            style = CoinStyles.DEFAULT

        self.coin_style = style

    def set_style(self, style=None, draw=None, color=None):
        """
        Update the tracker style
        """

        if self.active_style == style:
            return

        if not draw:
            draw = self.draw_style

        if not color:
            color = self.color

        if not style:
            style = self.coin_style

        draw.lineWidth = style.line_width
        draw.style = style.style
        draw.linePattern = style.line_pattern
        color.rgb = style.color

        if hasattr(self, 'marker'):
            self.marker.markerIndex = \
                Gui.getMarkerIndex(style.shape, style.size)

        self.active_style = style

    def finalize(self, node=None, parent=None):
        """
        Node destruction / cleanup
        """

        if node is None:
            node = self.get_node()

        self.remove_node(node, parent)

    def copy(self, node=None):
        """
        Return a copy of the tracker node
        """

        #copy operation assumes the geometry should not be controlled
        #by the node switch.  To copy with switch, call copy(self.get_node())
        if not node:
            node = self.node

        return node.copy()

    def insert_node(self, node, parent=None, index=None):
        """
        Insert a node as a child of the passed node
        """

        _idx = index
        _fn = None

        if not parent:
            if _idx is None:
                _idx = 0

            _fn = lambda _x: ViewState().sg_root.insertChild(_x, _idx)

        elif _idx is not None:
            _fn = lambda _x: parent.insertChild(_x, _idx)

        else:
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
