
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
from PySide import QtCore, QtGui
from freecad.trails import ICONPATH
from ..project.support import utils
import csv
import os


class ImportPointFile:
    """
    Command to import point file which includes survey data.
    """

    def __init__(self):
        """
        Constructor
        """

        # Set icon,  menu text and tooltip
        self.Resources = {
            'Pixmap': ICONPATH + '/icons/ImportPointFile.svg',
            'MenuText': "Import Point File",
            'ToolTip': "Import point file which includes survey data."
        }

        # Get file path
        self.Path = os.path.dirname(__file__)

        # Get *.ui file(s)
        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/ImportPointFile.ui")
        self.CPGui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreatePointGroup.ui")

        # UI connections
        UI = self.IPFui
        UI.AddB.clicked.connect(self.AddFile)
        UI.RemoveB.clicked.connect(self.RemoveFile)
        UI.SelectedFilesLW.itemSelectionChanged.connect(self.Preview)
        UI.PointGroupChB.stateChanged.connect(self.ActivatePointGroups)
        UI.CreateGroupB.clicked.connect(self.LoadCPGui)
        UI.ImportB.clicked.connect(self.ImportFile)
        UI.CancelB.clicked.connect(UI.close)

    def GetResources(self):
        """
        Return the command resources dictionary.
        """

        return self.Resources

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument is None:
            return False
        return True

    def Activated(self):
        """
        Command activation method
        """
        # Get or create 'Point_Groups' group
        try:
            PointGroups = FreeCAD.ActiveDocument.Point_Groups
        except Exception:
            FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Point_Groups')
            PointGroups = FreeCAD.ActiveDocument.Point_Groups
            PointGroups.Label = "Point Groups"

        # Get or create 'Points'
        try:
            Points = FreeCAD.ActiveDocument.Points
        except Exception:
            FreeCAD.ActiveDocument.addObject(
                'Points::Feature', "Points")
            Points = FreeCAD.ActiveDocument.Points
            PointGroups.addObject(Points)

        # Set and show UI
        UI = self.IPFui
        UI.setParent(FreeCADGui.getMainWindow())
        UI.setWindowFlags(QtCore.Qt.Window)
        UI.show()

        # Clear previous operation
        UI.FileNameL.setText("")
        UI.SubGroupListCB.clear()
        UI.SelectedFilesLW.clear()
        UI.PreviewTW.setRowCount(0)
        UI.PointGroupChB.setChecked(False)

        # Add point groups to QComboBox
        PointGroups = FreeCAD.ActiveDocument.Point_Groups.Group
        self.GroupList = []
        for Item in PointGroups:
            if Item.TypeId == 'Points::Feature':
                self.GroupList.append(Item.Name)
                UI.SubGroupListCB.addItem(Item.Label)

    def AddFile(self):
        """
        Add point files to importer
        """
        # Get selected point file(s) and add them to QListWidget
        UI = self.IPFui
        FileList = QtGui.QFileDialog.getOpenFileNames(
                        None, "Select one or more files to open",
                        os.getenv("HOME"), 'All Files (*.*)')
        UI.SelectedFilesLW.addItems(FileList[0])

    def RemoveFile(self):
        """
        Remove point files from importer
        """
        # Get selected point file(s) and remove them from QListWidget
        UI = self.IPFui
        for item in UI.SelectedFilesLW.selectedItems():
            UI.SelectedFilesLW.takeItem(UI.SelectedFilesLW.row(item))

    def ActivatePointGroups(self):
        """
        Enable or disable 'Create Point Group' feature
        """
        #If check box status changed, enable or disable combo box and push button.
        UI = self.IPFui
        if UI.PointGroupChB.isChecked():
            UI.SubGroupListCB.setEnabled(True)
            UI.CreateGroupB.setEnabled(True)
        else:
            UI.SubGroupListCB.setEnabled(False)
            UI.CreateGroupB.setEnabled(False)

    def LoadCPGui(self):
        """
        Load 'Create Point Group' UI.
        """
        # Set and show 'Create Point Group' UI
        UI = self.IPFui
        CPG = self.CPGui
        CPG.setParent(UI)
        CPG.setWindowFlags(QtCore.Qt.Window)
        CPG.show()

        # UI connections
        CPG.OkB.clicked.connect(self.CreatePointGroup)
        CPG.CancelB.clicked.connect(CPG.close)

    def CreatePointGroup(self):
        """
        Create new point group
        """
        # Create new point group and add it to QComboBox
        UI = self.IPFui
        CPG = self.CPGui
        NewGroupName = CPG.PointGroupNameLE.text()
        NewGroup = FreeCAD.ActiveDocument.addObject(
            'Points::Feature', "Point_Group")
        FreeCAD.ActiveDocument.Point_Groups.addObject(NewGroup)
        UI.SubGroupListCB.addItem(NewGroupName)
        self.GroupList.append(NewGroup.Name)
        NewGroup.Label = NewGroupName
        CPG.close()

    def FileReader(self, File, Operation):
        """
        Read file points and show them to user or add them to point group
        """
        # Get user inputs
        UI = self.IPFui
        self.PointList = []
        Counter = 1
        PointName = UI.PointNameLE.text()
        Northing = UI.NorthingLE.text()
        Easting = UI.EastingLE.text()
        Elevation = UI.ElevationLE.text()
        Description = UI.DescriptionLE.text()

        # Set delimiter
        if UI.DelimiterCB.currentText() == "Space":
            reader = csv.reader(File, delimiter=' ',
                skipinitialspace=True)

        if UI.DelimiterCB.currentText() == "Comma":
            reader = csv.reader(File, delimiter=',')

        if UI.DelimiterCB.currentText() == "Tab":
            reader = csv.reader(File, delimiter='\t')

        # Read files
        for row in reader:
            PN = int(PointName) - 1
            N = int(Northing) - 1
            E = int(Easting) - 1
            Z = int(Elevation) - 1
            D = int(Description) - 1

            # Show point file data in QTableView
            if Operation == "Preview":
                numRows = UI.PreviewTW.rowCount()
                UI.PreviewTW.insertRow(numRows)

                try:
                    UI.PreviewTW.setItem(
                        numRows, 0, QtGui.QTableWidgetItem(row[PN]))
                except Exception:
                    pass

                try:
                    UI.PreviewTW.setItem(
                        numRows, 1, QtGui.QTableWidgetItem(row[N]))
                except Exception:
                    pass

                try:
                    UI.PreviewTW.setItem(
                        numRows, 2, QtGui.QTableWidgetItem(row[E]))
                except Exception:
                    pass

                try:
                    UI.PreviewTW.setItem(
                        numRows, 3, QtGui.QTableWidgetItem(row[Z]))
                except Exception:
                    pass

                try:
                    UI.PreviewTW.setItem(
                        numRows, 4, QtGui.QTableWidgetItem(row[D]))
                except Exception:
                    pass

                if Counter == 500:
                    break
                else:
                    Counter += 1

            # Add points to point group
            elif Operation == "Import":
                try:
                    self.PointList.append((float(row[E]) * 1000,
                                           float(row[N]) * 1000,
                                           float(row[Z]) * 1000))
                except Exception:
                    pass

    def Preview(self):
        """
        Show a preview for selected point file
        """
        # Get selected file
        UI = self.IPFui
        listItems = UI.SelectedFilesLW.selectedItems()

        # Separate path and file name
        if listItems:
            head, tail = os.path.split(listItems[0].text())
            UI.FileNameL.setText(tail)
            UI.PreviewTW.setRowCount(0)

            # Send selected point file to preview
            File = open(listItems[0].text(), 'r')
            self.FileReader(File, "Preview")

    def ImportFile(self):
        """
        Import added files to selected point group
        """
        # Get user inputs
        UI = self.IPFui
        Index = UI.SubGroupListCB.currentIndex()

        # If check box is checked get selected item in QComboBox
        if UI.PointGroupChB.isChecked():
            SPG = self.GroupList[Index]
            PointGroup = FreeCAD.ActiveDocument.getObject(SPG)
        else:
            PointGroup = FreeCAD.ActiveDocument.Points

        # Read Points from file
        if UI.SelectedFilesLW.count() < 1:
            FreeCAD.Console.PrintMessage("No Files selected")
            return

        Items = []
        for i in range(UI.SelectedFilesLW.count()):
            Items.append(UI.SelectedFilesLW.item(i))
        Labels = [i.text() for i in Items]
        for FilePath in Labels:
            File = open(FilePath, 'r')
            self.FileReader(File, "Import")

        List = []
        fpoint = self.PointList[0]
        base = FreeCAD.Vector(fpoint[0], fpoint[1], fpoint[2])
        nbase = utils.rendering_fix(base)

        for Point in self.PointList:
            Point = (Point[0]-nbase.x, Point[1]-nbase.y, Point[2]-nbase.z)
            List.append(Point)

        PointObject = PointGroup.Points.copy()
        PointObject.addPoints(List)
        PointGroup.Points = PointObject
        PointGroup.Placement.move(nbase)
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        UI.close()

FreeCADGui.addCommand('Import Point File', ImportPointFile())
