# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2018 Joel Graff <monograff76@gmail.com>               *
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
Publisher Events class
"""

import types

from inspect import getmro

from ...support.const import Const

class _EVT(Const):

    #8 possible event groups
    MSB = 3
    LSB = 2**MSB

    @staticmethod
    def get(base, num):
        """Calc the base-2 flag value"""
        return base + num * _EVT.LSB

    @staticmethod
    def get_enum():
        """Return a new object for enumeration"""
        return types.SimpleNamespace()

class EvtBase(Const):
    """
    Provide the same data strcutres for every class.  These are non-const
    """

    @staticmethod
    def vals(ns, obj):
        """
        Return the data structures for enumeration
        """

        setattr(ns, '_EVENTS', {
            _k:_e for _k, _e in obj.__dict__.items()\
                if _k[0] != '_' and _k != 'enum'
        })

        setattr(ns, '_NAMES', [_k for _k in ns._EVENTS])

        if PublisherEvents in getmro(obj):
            setattr(ns, '_VALUES', [_v.EVENTS for _v in ns._EVENTS.values()])

        else:
            setattr(ns, '_VALUES', [_v for _v in ns._EVENTS.values()])

        return ns

class PublisherEvents(Const):
    """
    Events for Publisher class
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # PUBLISHER EVENTS
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    # Events are categorized by object type
    # Event names and tenses indicate nature and direction of the event.
    # Message should contain context-specific data w.r.t event type.
    #
    # For example, the NodeTracker accepts NODE.SELECT / NODE.UPDATE
    # events and dispatches NODE.SELECTED / NODE.UPDATED events.
    # Corresponding data would be a single coordinate tuple.
    #
    # Categories:
    # -----------
    #   ALL - Represents all events that may be transmitted / received
    #   TASK
    #   TRACKER
    #   NODE
    #   CURVE
    #   ALIGNMENT
    #
    # Events:
    # -------
    #   EVENTS - All events for that category
    #   SELECT / SELECTED - Object to be / has been selected
    #   UPDATE / UPDATED - Object to be / has been updated
    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    enum = _EVT.get_enum()

    class ALL(Const):
        """ALL Events"""

        EVENTS = 0
        SELECTED = _EVT.get(EVENTS, 1)
        UPDATED = _EVT.get(EVENTS, 2)
        UPDATE = _EVT.get(EVENTS, 3)
        enum = _EVT.get_enum()


    class TASK(Const):
        """TASK Events"""

        EVENTS = 1
        UPDATED = _EVT.get(EVENTS, 1)
        enum = _EVT.get_enum()

    class TRACKER(Const):
        """TRACKER Events"""

        EVENTS = 2
        enum = _EVT.get_enum()

    class GEOMETRY(Const):
        """GEOMETRY Events"""

        EVENTS = 3
        SELECTED = _EVT.get(EVENTS, 1)
        UPDATED = _EVT.get(EVENTS, 2)
        APPLY_PATHING = _EVT.get(EVENTS, 3)
        enum = _EVT.get_enum()

    class NODE(Const):
        """NODE Events"""

        EVENTS = 3
        UPDATED = _EVT.get(EVENTS, 1)
        SELECTED = _EVT.get(EVENTS, 2)
        UPDATE = _EVT.get(EVENTS, 3)
        enum = _EVT.get_enum()

    class WIRE(Const):
        """WIRE Events"""

        EVENTS = 4
        enum = _EVT.get_enum()

    class CURVE(Const):
        """CURVE Events"""

        EVENTS = 5
        SELECTED = _EVT.get(EVENTS, 1)
        UPDATED = _EVT.get(EVENTS, 2)
        UPDATE = _EVT.get(EVENTS, 3)
        enum = _EVT.get_enum()

    class ALIGNMENT(Const):
        """ALIGNMENT Events"""

        EVENTS = 6
        UPDATED = _EVT.get(EVENTS, 1)
        UPDATE = _EVT.get(EVENTS, 2)
        enum = _EVT.get_enum()

EvtBase.vals(PublisherEvents.enum, PublisherEvents)
EvtBase.vals(PublisherEvents.ALL.enum, PublisherEvents.ALL)
EvtBase.vals(PublisherEvents.TASK.enum, PublisherEvents.TASK)
EvtBase.vals(PublisherEvents.TRACKER.enum, PublisherEvents.TRACKER)
EvtBase.vals(PublisherEvents.GEOMETRY.enum, PublisherEvents.GEOMETRY)
EvtBase.vals(PublisherEvents.NODE.enum, PublisherEvents.NODE)
EvtBase.vals(PublisherEvents.WIRE.enum, PublisherEvents.WIRE)
EvtBase.vals(PublisherEvents.CURVE.enum, PublisherEvents.CURVE)
EvtBase.vals(PublisherEvents.ALIGNMENT.enum, PublisherEvents.ALIGNMENT)
