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
View state class
"""

from pivy import coin

import FreeCADGui as Gui

from .singleton import Singleton

class ViewState(metaclass=Singleton):
    """
    Class to track the current state of the active or specified view
    """

    def __init__(self, view=None):
        """
        ViewState constructor
        """

        if not view:
            view = Gui.ActiveDocument.ActiveView

        self.view = view
        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()
        self.sg_root = self.view.getSceneGraph()

        self._matrix = None

    def get_matrix(self, node, parent=None, refresh=True):
        """
        Return the matrix for transfomations applied to the passed node

        node - the node with the desired transformation
        parent - optional - sg root default
        refresh - if false, retrieves last matrix
        """

        if not parent:
            parent = self.sg_root

        if not refresh:
            if self._matrix:
                return self._matrix

        #define the search path
        _search = coin.SoSearchAction()
        _search.setNode(node)
        _search.apply(parent)

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(ViewState().viewport)
        _matrix.apply(_search.getPath())

        self._matrix = coin.SbMatrix(_matrix.getMatrix().getValue())

        return self._matrix