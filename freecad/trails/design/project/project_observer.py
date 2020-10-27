# -*- coding: utf-8 -*-
#***********************************************************************
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
Observer class to manage document level events
"""
import FreeCAD as App


class ProjectObserver(object):
    """
    Observer class to manage serializing XML to FCStd file
    """
    docs = {}

    @staticmethod
    def get(doc):
        """
        Factory method to create an observer attached to doc
        If already created, return it
        """

        if not doc in ProjectObserver.docs:

            ProjectObserver.docs[doc] = ProjectObserver(doc)
            App.addDocumentObserver(ProjectObserver.docs[doc])

        return ProjectObserver.docs[doc]

    def __init__(self, doc):
        """
        Constructor
        """
        self.doc = doc
        self.targets = {'StartSaveDocument': []}

    def register(self, event_name, callback):
        """
        Registration for target objects to be updated for specific tasks
        """

        self.targets[event_name].append(callback)

    def slotStartSaveDocument(self, doc, file):
        """
        Administrative work to do before saving a document
        """

        if not doc == self.doc:
            return

        for _cb in self.targets['StartSaveDocument']:
            _cb()

    def slotDeletedDocument(self, doc):
        """
        Remove observer when document is destroyed
        """
        if not doc == self.doc:
            return

        App.removeDocumentObserver(self)
