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

import math

from enum import IntEnum

from pivy import coin

from PySide.QtGui import QCursor
from PySide import QtGui
from PySide.QtCore import Qt

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
        self.conditions = []

        self.matrix = None

        self.drag_group = None

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

        #bypass overrides on initialization
        BaseTracker.set_style(self, CoinStyles.DEFAULT)
        BaseTracker.set_visible(self, True)

    def is_selected(self):
        """
        Return selection state
        """

        return SelectState().exists(self)

    def refresh(self, style=None, visible=None):
        """
        Update the tracker to reflect state changes
        """

        if not style:

            style = self.coin_style

            if self.is_selected():
                style = CoinStyles.SELECTED

        self._process_conditions()
        self.set_style(style)
        self.set_visible(visible)

    def mouse_event(self, arg):
        """
        SoLocation2Event callback
        """

        #pre-emptive abort conditions
        if not self.state.enabled.value:
            return

        if not self.state.visible.value:

            self.refresh()

            if not self.state.visible.value:
                return

        self.update_dragging()
        self.update_highlighting()

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        #preemptive abort if not both enabled and visible
        if not (self.state.enabled.value and self.state.visible.value):
            return

        if MouseState().button1.state == 'DOWN':
            SelectState().update(self)

        self.refresh()

    def update_highlighting(self):
        """
        Test for highlight conditions and changes
        """

        if self.state.dragging or self.is_selected():
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

            print(self.name, 'base update drag')
            if not self.state.dragging:

                self.start_drag()

            else:
                self.on_drag()

        #otherwise, end_drag is the only option
        elif self.state.dragging:

            self.end_drag()
            self.state.dragging = False

    def start_drag(self):
        """
        Initialize drag ops
        """

        #copy the tracker node structure to the drag state node for
        #transformations during drag operations

        self.drag_group = DragState().add_node(self.copy())
        self.state.dragging = True

        if self.name == MouseState().component:

            DragState().node = self
            DragState().start = MouseState().coordinates
            DragState().coordinates = MouseState().coordinates
            DragState().insert()

    def on_drag(self):
        """
        Ongoing drag ops
        """

        if not self.state.dragging or self != DragState().node:
            return

        #if DragState().override:
        #    return

        _scale = 1.0

        if MouseState().shiftDown:
            _scale = 0.10

        _drag_line_start = DragState().start
        _drag_line_end = MouseState().coordinates
        _mouse_coord = MouseState().coordinates

        #rotation transformation
        if MouseState().altDown:

            DragState().rotate(_mouse_coord, MouseState().shiftDown)

            _ctr = Vector(DragState().node_rotate.center.getValue())
            _offset = Vector(DragState().node_translate.translation.getValue())

            _drag_line_start = _ctr.add(_offset)

            _mouse_coord = DragState().coordinates

        #translation transformation
        else:
            DragState().translate(_mouse_coord, MouseState().shiftDown)

        #micro-dragging cursor control
        if MouseState().shiftDown:

            QtGui.QApplication.setOverrideCursor(Qt.BlankCursor)

            #get the window position of the updated drag delta coordinate
            _mouse_coord = DragState().start.add(DragState().delta)
            _new_pos = ViewState().getPointOnScreen(_mouse_coord)

            #set the mouse position at the updated screen coordinate
            _delta_pos = _new_pos.sub(Vector(MouseState().pos + (0.0,)))

            #get screen position by adding offset to the new window position
            _pos = Vector(QCursor.pos().toTuple() + (0.0,)).add(
                Vector(_delta_pos.x, -_delta_pos.y))

            QCursor.setPos(_pos[0], _pos[1])

        #no micro-drag?  shut off cursor override
        elif QtGui.QApplication.overrideCursor():
            QtGui.QApplication.restoreOverrideCursor()

        #save the drag state coordinate as the current mouse coordinate
        DragState().coordinates = _mouse_coord
        DragState().update(_drag_line_start, _drag_line_end)

    def end_drag(self):
        """
        Terminate drag ops
        """

        if not self.state.dragging:
            return

        DragState().finish()

        if QtGui.QApplication.overrideCursor() == Qt.BlankCursor:
            QtGui.QApplication.restoreOverrideCursor()

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
        Process the conditions which determine node visibility
        """

        if self.state.visible.ignore or not self.conditions:
            return

        _c = MouseState().component

        self.set_visible(True)

        for _cond in self.conditions:

            if (_cond[0] == '!' and _cond[1:] not in _c) or (_cond in _c):

                self.set_visible(False)
                break

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
