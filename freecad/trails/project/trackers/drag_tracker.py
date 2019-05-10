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
Tracker for dragging operations
"""

from pivy import coin

from FreeCAD import Vector

from DraftGui import todo

from .base_tracker import BaseTracker

class DragTracker(BaseTracker):
    """
    Tracker for dragging operations
    """

    def __init__(self, names, trackers, selected, picked_name):
        """
        Constructor
        names - list of names for BaseTracker
        trackers - dict of all node trackers
        selected - dict of selected trackers
        picked_name - name of tracker picked at start of drag
        """

        self.trackers = {
            'start': None,
            'selected': self.sort_selected(selected),
            'end': None
        }

        picked = trackers[picked_name]

        self.connector_coord = None
        self.switch = coin.SoSwitch()
        self.transform = coin.SoTransform()
        self.transform.translation.setValue([0.0, 0.0, 0.0])

        #get ordered list of trackers, including preceding and following
        self.build_tracker_dict(trackers, selected)

        self.connector_group = self.build_connector_group()

        self.selected_group = self.build_selected_group()

        super().__init__(
            names, [self.connector_group], False #, self.selected_group],
            #False
        )

        self.datum = Vector(picked.coord.point.getValues()[0].getValue())

        self.switch.addChild(self.node)

        self.on(self.switch)

    def sort_selected(self, selected):
        """
        Iterate the selected group of trackers and ensure they are
        in the proper order
        """

        name_list = [_v.name for _v in selected]
        name_list.sort()

        result = []

        for _n in name_list:
            for _t in selected:
                if _t.name == _n:
                    result.append(_t)
                    break

        return result

    def build_selected_group(self):
        """
        Build the SoGroup node which provides transformation for the
        SoMarkerSet and SoLineSet that represents the selected geometry
        """

        #create list of each coordinate duplicated
        coordinates = []

        if not self.trackers['selected']:
            return None

        count = len(self.trackers['selected']) - 1

        for _i, _v in enumerate(self.trackers['selected']):

            _c = list(_v.get())

            coordinates.append(_c)

            if _i == 0 or _i == count:
                continue

            coordinates.append(_c)

        count = len(coordinates)

        verts = [2]*int(count/2)

        coord = coin.SoCoordinate3()

        print('\n\t----> coords: ', coordinates, '\n\tcount: ', count)

        coord.point.setValues(0, count, coordinates)

        marker = coin.SoMarkerSet()

        line = coin.SoLineSet()
        line.numVertices.setValues(verts)

        #build node and add children
        group = coin.SoGroup()
        group.addChild(self.transform)
        group.addChild(coord)
        group.addChild(marker)
        group.addChild(line)

        return group

    def build_connector_group(self):
        """
        Build the SoGroup node which provides the connecting SoLineSet
        geometry to the geometry which is not being selected / dragged
        """


        trackers = [self.trackers['start'],
                    self.trackers['selected'][0],
                    self.trackers['end']
                      ]

        verts = []

        if trackers[0]:
            verts.append(2)

        if trackers[2]:
            verts.append(2)

        #abort if we don't have at least two coordinates defined
        if len([_c for _c in trackers if _c]) < 2:
            return None

        count = len(trackers) - 1

        coordinates = []

        #replace None values
        for _i, _v in enumerate(trackers):

            _c = list(_v.get())

            coordinates.append(_c)

            if _i == 0 or _i == count:
                continue

            coordinates.append(_c)

        coord = coin.SoCoordinate3()
        coord.point.setValues(0, len(coordinates), coordinates)

        marker = coin.SoMarkerSet()

        line = coin.SoLineSet()

        line.numVertices.setValues(verts)

        group = coin.SoGroup()
        group.addChild(coord)
        group.addChild(marker)
        group.addChild(line)

        return group

    def build_tracker_dict(self, trackers, selected):
        """
        Build the dictionary of trackers
        """

        #TODO: this should not be necessary - dict should only be node trackers
        #at the start.
        sel_list = [_v.name for _v in selected]
        sel_list.sort()

        key_list = list(trackers.keys())
        key_list.sort()

        _start = int(sel_list[0].split('-')[1])
        _end = int(sel_list[-1].split('-')[1])

        #if our starting node isn't the first, add the previous node
        if _start > 0:
            self.trackers['start'] = trackers[key_list[_start - 1]]

        #if our ending node isn't the last, add the next node
        if _end < len(trackers) - 1:
            self.trackers['end'] = trackers[key_list[_end + 1]]

    def update(self, position):
        """
        Update the transform with the passed position
        """

        self.connector_coord.point.setValue(tuple(position))
        self.transform.translation.setValue(tuple(position))

    def update_placement(self, position):
        """
        Update the placement
        """

        _pos = tuple(position.sub(self.datum))
        self.transform.translation.setValue(_pos)

    def get_placement(self):
        """
        Return the placement of the tracker
        """

        return Vector(self.transform.translation.getValue())

    def finalize(self, node=None):
        """
        Shutdown
        """

        if not node:
            node = self.switch

        todo.delay(self.parent.removeChild, node)
