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

from pivy import coin

from DraftTrackers import Tracker

from ..support.utils import Constants as C


class BaseTracker(Tracker):
    """
    Customized wire tracker
    """

    def __init__(self, doc, object_name, node_name, nodes=None):

        self.name = node_name
        self.object_name = object_name

        self.inactive = False

        self.color = coin.SoBaseColor()
        self.marker = coin.SoMarkerSet()
        self.coords = coin.SoCoordinate3()

        selnode  = coin.SoType.fromName("SoFCSelection").createInstance()
        selnode.documentName.setValue(doc.Name)
        selnode.objectName.setValue(object_name)
        selnode.subElementName.setValue(node_name)

        selnode.addChild(self.coords)
        selnode.addChild(self.color)
        selnode.addChild(self.marker)

        node = coin.SoAnnotation()
        node.addChild(selnode)

        child_nodes = nodes

        if not isinstance(nodes, list):
            child_nodes = [nodes]

        child_nodes += [node]

        Tracker.__init__(
            self, children=child_nodes + [node],
            ontop=True, name="EditTracker")
