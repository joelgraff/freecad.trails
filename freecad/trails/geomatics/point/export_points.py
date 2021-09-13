# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
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

import FreeCAD
import FreeCADGui
from PySide2 import QtCore, QtGui, QtWidgets
from freecad.trails import ICONPATH
from . import point_groups
import os

class ExportPoints:
    """
    Command to export points to point file.
    """

    def __init__(self):
        """
        Constructor
        """
        # Get file path
        ui_path = os.path.dirname(__file__)

        # Get *.ui file(s)
        ui = FreeCADGui.PySideUic.loadUi(ui_path + "/export_points.ui")

        # UI connections
        ui.BrowseB.clicked.connect(self.file_destination)
        ui.ExportB.clicked.connect(self.export_points)
        ui.CancelB.clicked.connect(ui.close)
        self.ui = ui

    def GetResources(self):
        """
        Return the command resources dictionary.
        """

        return {
            'Pixmap': ICONPATH + '/icons/ExportPoints.svg',
            'MenuText': "Export Points",
            'ToolTip': "Export points to point file."
            }

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            return True
        return False

    def Activated(self):
        """
        Command activation method
        """
        # Create 'Point_Groups' group
        groups = point_groups.get()

        # Set and show UI
        self.ui.setParent(FreeCADGui.getMainWindow())
        self.ui.setWindowFlags(QtCore.Qt.Window)
        self.ui.show()

        # Clear previous operation
        self.ui.FileDestinationLE.clear()
        self.ui.PointGroupsLW.clear()

        # Add point groups to QListWidget
        self.group_dict = {}
        for child in groups.Group:
            if child.Proxy.Type == 'Trails::PointGroup':
                self.group_dict[child.Label] = child
                self.ui.PointGroupsLW.addItem(child.Label)

    def file_destination(self):
        """
        Get file destination.
        """
        # Select file
        parameter = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General")
        path = parameter.GetString("FileOpenSavePath")
        file_name = QtWidgets.QFileDialog.getSaveFileName(
            None, 'Save File', path, Filter='*.txt')

        # Add ".txt" if needed
        if file_name[0][-4:] == ".txt":
            fn = file_name[0]
        else:
            fn = file_name[0] + ".txt"

        self.ui.FileDestinationLE.setText(fn)

    def export_points(self):
        """
        Export selected point group(s).
        """
        # Get user inputs
        line_edit = self.ui.FileDestinationLE
        point_name = self.ui.PointNameLE.text()
        northing = self.ui.NorthingLE.text()
        easting = self.ui.EastingLE.text()
        elevation = self.ui.ElevationLE.text()
        description = self.ui.DescriptionLE.text()
        format = ["", "", "", "", ""]

        if line_edit.text().strip() == "" or self.ui.PointGroupsLW.count() < 1:
            return

        # Set delimiter
        if self.ui.DelimiterCB.currentText() == "Space":
            delimiter = ' '
        elif self.ui.DelimiterCB.currentText() == "Comma":
            delimiter = ','

        # Create point file
        try:
            file = open(line_edit.text(), 'w')
        except Exception:
            FreeCAD.Console.PrintMessage("Can't open file")

        counter = 1
        # Get selected point groups
        for selection in self.ui.PointGroupsLW.selectedIndexes():
            group = self.group_dict[selection.data()]

            # Print points to the file
            for point in group.Points:
                xx = str(round(float(point.x) / 1000, 3))
                yy = str(round(float(point.y) / 1000, 3))
                zz = str(round(float(point.z) / 1000, 3))
                index = group.Points.index(point)
                if group.PointNames:
                    pn = group.PointNames[index]
                else:
                    pn = counter
                    counter += 1

                if group.Descriptions:
                    des = group.Descriptions[index]
                else: des = ''

                format[int(point_name)-1] = pn
                format[int(easting)-1] = xx
                format[int(northing)-1] = yy
                format[int(elevation)-1] = zz
                format[int(description)-1] = des

                file.write(delimiter.join(format) +"\n")
        file.close()

FreeCADGui.addCommand('Export Points', ExportPoints())
