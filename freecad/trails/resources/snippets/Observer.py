# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

import FreeCAD as App
import FreeCADGui as Gui
import random

from Project.Support import Singleton

def create(doc, callback):
    """
    Creation method for _Document class
    """
    if _saveObserver.instance() is None:
        App.addDocumentObserver(_saveObserver(doc))
    else:
        _saveObserver.instance().set_document(doc)

class _saveObserver(metaclass=Singleton.Singleton):

    def __init__(self, doc, callback):

        self.target_doc = doc
        self.callback = callback

    def set_document(self, doc):
        """
        Set the passed document as the active document for the observer
        """

        self.target_doc = doc

    @staticmethod
    def instance():
        """
        Return the singleton instance of the class
        """

        return Singleton.Singleton.instance_of(_saveObserver)

    def slotStartSaveDocument(self, doc, value):

        print('calling save document...', doc.Label, value)

        if _saveObserver.instance() is None:
            App.removeDocumentObserver(self)
            return

        #if the document is deleted, remove the observer
        try:
            self.target_doc.__doc__
        except:
            App.removeDocumentObserver(self)
            return

        if doc == self.target_doc:
            self.target_doc.before_save('slotStartSaveDocument')
