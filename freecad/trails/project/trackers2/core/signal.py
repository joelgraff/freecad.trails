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
Publisher / Subscriber services for Tracker objects
"""

from .publisher import Publisher
from .subscriber import Subscriber

class Signal(Publisher, Subscriber):
    """
    Publisher / Subscriber services for Tracker objects
    """

    #Global constant defaults for enabling / disabling signaling
    #To be overridden in inheriting classes to selectively disable
    SIGNAL_PUBLISH = True
    SIGNAL_SUBSCRIBE = True

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.do_publish = self.SIGNAL_PUBLISH
        self.do_subscribe = self.SIGNAL_SUBSCRIBE

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # PUBLISHER INTERFACE
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_subscribers(self, events=0):
        """Override base implementation"""

        if self.do_publish:
            Publisher.get_subscribers(self, events)

    def register(self, who, events, callback=None):
        """Override base implementation"""

        if self.do_publish:
            Publisher.register(self, who, events, callback)

    def unregister(self, who, events):
        """Override base implementation"""

        if self.do_publish:
            Publisher.unregister(self, who, events)


    def dispatch(self, event, message, verbose=False):
        """Override base implementation"""

        if self.do_publish:
            Publisher.dispatch(self, event, message, verbose)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # SUBSCRIBER INTERFACE
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def notify(self, event_type, message, verbose=False):
        """Override base implementation"""

        if self.do_subscribe:
            Subscriber.notify(self, event_type, message, verbose)
