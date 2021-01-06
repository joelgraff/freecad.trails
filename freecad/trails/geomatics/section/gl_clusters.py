# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

'''
Create a Guide Line Clusters group object from FPO.
'''

import FreeCAD
from freecad.trails import ICONPATH, geo_origin



def get():
    """
    Find the existing Guide Line Clusters group object
    """
    # Return an existing instance of the same name, if found.
    obj = FreeCAD.ActiveDocument.getObject('GuideLineClusters')

    if obj:
        return obj

    obj = create()

    return obj

def create():
    """
    Factory method for Guide Line Clusters.
    """
    main = geo_origin.get()
    alignments = FreeCAD.ActiveDocument.getObject('Alignments')
    alignment_group = FreeCAD.ActiveDocument.getObject('AlignmentGroup')
    if alignments: alignment_group = alignments
    elif not alignment_group:
        alignment_group = FreeCAD.ActiveDocument.addObject(
            "App::DocumentObjectGroup", 'AlignmentGroup')
        alignment_group.Label = "Alignment Group"
        main.addObject(alignment_group)

    obj = FreeCAD.ActiveDocument.addObject(
        "App::DocumentObjectGroupPython", 'GuideLineClusters')
    obj.Label = "Guide Line Clusters"
    alignment_group.addObject(obj)

    GuideLineClusters(obj)
    ViewProviderGuideLineClusters(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()

    return obj


class GuideLineClusters:
    """
    This class is about Guide Line Clusters object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''
        self.Type = 'Trails::GuideLineClusters'

        obj.Proxy = self

    def onChanged(self, fp, prop):
        '''
        Do something when a data property has changed.
        '''
        return

    def execute(self, fp):
        '''
        Do something when doing a recomputation. 
        '''
        return


class ViewProviderGuideLineClusters:
    """
    This class is about Guide Line Clusters object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        self.Object = vobj.Object
        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        self.Object = vobj.Object
        return

    def getIcon(self):
        '''
        Return object treeview icon.
        '''
        return ICONPATH + '/icons/GuideLines.svg'

    def claimChildren(self):
        """
        Provides object grouping
        """
        return self.Object.Group

    def setEdit(self, vobj, mode=0):
        """
        Enable edit
        """
        return True

    def unsetEdit(self, vobj, mode=0):
        """
        Disable edit
        """
        return False

    def doubleClicked(self, vobj):
        """
        Detect double click
        """
        pass

    def setupContextMenu(self, obj, menu):
        """
        Context menu construction
        """
        pass

    def edit(self):
        """
        Edit callback
        """
        pass

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None
 
    def __setstate__(self,state):
        """
        Get variables from file.
        """
        return None