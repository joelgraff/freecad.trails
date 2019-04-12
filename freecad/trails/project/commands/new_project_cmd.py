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
Command to create a new Trails project
"""
import os

import FreeCAD as App
import FreeCADGui as Gui

from PySide import QtGui, QtCore

from ..support import document_properties
from ... import resources, corridor

class NewProject():
    """
    Command to creatae a new Trails project
    """
    icon_path = os.path.dirname(resources.__file__)

    resources = {
        'Pixmap'  : icon_path + '/icons/workbench.svg',
        'Accel'   : "Shift+N",
        'MenuText': "New Project",
        'ToolTip' : "Create a new project document and make it active",
        'CmdType' : "ForEdit"
    }

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return self.resources

    def Activated(self):
        """
        Activation callback
        """
        if not Gui.ActiveDocument:
            self._create_document()

        self._set_preferences()
        return

    def IsActive(self):
        """
        Returns always active
        """
        return True

    @staticmethod
    def _attach_handlers():
        pass
        #Gui.ActiveDocument.ActiveView.addDraggable

    @staticmethod
    def _set_preferences():
        App.ParamGet(
            "User parameter:BaseApp/Preferences/Units"
        ).SetInt("UserSchema", 7)

        App.ParamGet(
            'User parameter:BaseApp/Preferences/Mod/Sketcher'
        ).SetBool('AutoRecompute', False)

        App.ParamGet(
            'User parameter:BaseApp/Preferences/Document'
        ).SetBool('DuplicateLabels', True)

        template_path = os.path.dirname(corridor.__file__)

        document_properties.TemplateLibrary.Path.set_value(
            template_path + '/Templates'
            )

    def _create_document(self):

        """
        Create a new project with default groups
        """

        #new project dialog
        dlg = QtGui.QInputDialog()
        dlg.setWindowTitle("New Proejct")
        dlg.setLabelText('Enter project name:')
        dlg.setWindowModality(QtCore.Qt.ApplicationModal)
        dlg.setTextValue('New Project')
        dlg.exec_()

        if not dlg.result():
            return

        #assign project name, null names not accepted.
        project_name = dlg.textValue()

        if not project_name:
            return

        App.newDocument(project_name)

        #substitute underscores for spaces for internal naming
        project_name = project_name.replace(' ', '_')

        #set up intial references
        App.setActiveDocument(project_name)

        App.ActiveDocument = App.getDocument(project_name)
        Gui.ActiveDocument = Gui.getDocument(project_name)

        #create default groups
        App.ActiveDocument.addObject('App::DocumentObjectGroup', 'Templates')
        App.ActiveDocument.addObject('App::DocumentObjectGroup', 'Alignments')
        App.ActiveDocument.addObject(
            'App::DocumentObjectGroup', 'Element Lofts'
        )

        #create observers to handle tasks when document-level events occur
        #Observer.create(App.ActiveDocument)

Gui.addCommand('NewProject', NewProject())
