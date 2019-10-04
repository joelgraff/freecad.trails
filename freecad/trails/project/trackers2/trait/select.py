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
Provides SoFCSelection support for Tracker classes
"""

from pivy import coin

from ..support.select_state import SelectState

from .coin.coin_styles import CoinStyles
from .coin.coin_enums import MouseEvents

from .event import Event
#from ..support.publisher_events import PublisherEvents as Events

class Select():
    """
    Provides SoFCSelection support for Tracker classes
    """

    #Base, Style and Event prototypes
    name = None
    names = []
    base = None
    mouse_state = None
    coin_style = None
    active_style = None
    event_class = None

    def set_style(self, style=None, draw=None, color=None):
        """prototype"""; pass

    def add_event_callback(self, event_type, callback, node=None, index=-1):
        """prototype"""; pass

    def add_mouse_event(self, callback): """prototype"""; pass
    def add_button_event(self, callback): """prototype"""; pass

    #class static for global selection
    select_state = SelectState()
    callback_node = None

    def __init__(self):
        """
        Constructor
        """
        #Pylint doesn't see self.base members...
        #pylint: disable=no-member

        if not self.names:
            return

        self.do_select_highlight = True

        self.select = coin.SoType.fromName("SoFCSelection").createInstance()

        self.select.documentName.setValue(self.names[2])
        self.select.objectName.setValue(self.names[1])
        self.select.subElementName.setValue(self.names[0])

        self.select.setName(self.name + '__SELECT')
        self.base.insert_node(self.select, self.base.top)

        #add the default select callback nodes to the first selectable
        #tracker that's created.
        if not Select.callback_node:

            Select.callback_node = Event._default_callback_node

            Select.callback_node.addEventCallback(
                MouseEvents.LOCATION2, self._select_mouse_event)

            Select.callback_node.addEventCallback(
                MouseEvents.MOUSE_BUTTON, self._select_button_event)

        super().__init__()

    def is_selected(self):
        """
        Return whether or not the node is selected at all
        """

        return self.select_state.is_selected(self) > SelectState.States.NONE

    def _select_mouse_event(self, user_data, event_cb):
        """
        Global mouse event
        """

        print(self.name, 'global select mouse')
        self.select_state.set_highlight()

    def _select_button_event(self, user_data, event_cb):
        """
        Global button event
        """

        print(self.name, 'global select button')

    def select_mouse_event(self, user_data, event_cb):
        """
        Mouse override
        """

        if self.is_selected():
            self.set_style(CoinStyles.SELECTED)

        else:
            self.update_highlight()

    def update_highlight(self):
        """
        Update the highlight condition of the node
        """

        if self.do_select_highlight \
            and self.name == self.mouse_state.component:

            self.set_style(CoinStyles.SELECTED)

    def select_button_event(self, user_data, event_cb):
        """
        Mouse override
        """

        _style = self.coin_style

        print(self.name, 'do select ', str(self.mouse_state.button1), event_cb)
        #on button down, do selection
        if self.mouse_state.button1.pressed:

            self.select_state.select(
                self, self.mouse_state.component, self.mouse_state.ctrl_down)

            if self.is_selected():
                _style = CoinStyles.SELECTED

                #if self.base.do_publish:
                #    self.base.notify(Events.GEOMETRY.SELECTED, (self.name,
                #None))

        #on button up, highlight, if hovering over
        elif self.is_selected():
            _style = CoinStyles.SELECTED

        elif self.do_select_highlight:

            if self.name == self.mouse_state.component:
                _style = CoinStyles.SELECTED

        self.set_style(_style)
