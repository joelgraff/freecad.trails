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

from .coin_styles import CoinStyles

from .mouse import Mouse
from .signal import Signal

from .select_state import SelectState
from .select_state import SelectStateEnum as Enum

from .publisher_events import PublisherEvents as Events

class Select(Mouse, Signal):
    """
    Provides SoFCSelection support for Tracker classes
    """

    #members provided by Base, Style, and 
    name = None
    names = []
    base_node = None
    coin_style = None
    active_style = None
    event_class = None

    def set_style(self, style=None, draw=None, color=None): pass

    #class static for global selection
    sel_state = SelectState()

    def __init__(self):
        """
        Constructor
        """

        if not self.names:
            return

        self.do_select_highlight = True

        self.sel_node = coin.SoType.fromName("SoFCSelection").createInstance()

        self.sel_node.documentName.setValue(self.names[2])
        self.sel_node.objectName.setValue(self.names[1])
        self.sel_node.subElementName.setValue(self.names[0])

        self.base_node.addChild(self.sel_node)

        super().__init__()

    def is_selected(self):
        """
        Return whether or not the node is selected at all
        """

        return self.sel_state.is_selected(self) > Enum.NONE

    def mouse_event(self, arg):
        """
        Mouse override
        """

        _style = self.coin_style

        if self.is_selected():
            _style = CoinStyles.SELECTED

        elif self.do_select_highlight \
            and self.name == self.mouse_state.component:

            _style = CoinStyles.SELECTED

        Mouse.mouse_event(self, arg)

        self.set_style(_style)

    def button_event(self, arg):
        """
        Mouse override
        """

        _style = self.coin_style

        #on button down, do selection
        if self.mouse_state.button1.state == 'DOWN':

            self.sel_state.select(self, self.mouse_state.component)

            if self.is_selected():
                _style = CoinStyles.SELECTED

                if self.do_publish:
                    self.notify(Events.GEOMETRY.SELECTED, (self.name, None))

        #on button up, highlight, if hovering over
        elif self.is_selected():
            _style = CoinStyles.SELECTED

        elif self.do_select_highlight:

            if self.name == self.mouse_state.component:
                _style = CoinStyles.SELECTED

        self.set_style(_style)

        Mouse.button_event(self, arg)
