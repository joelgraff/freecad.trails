from PySide import QtGui, QtCore
import FreeCAD as App
import FreeCADGui as Gui
import Part

userCancelled = "Cancelled"
userOk = "OK"

class SweepPicker(QtGui.QMainWindow):

    class SelectionObserver:

        def setDialog(self, dialog):
            self.dialog = dialog

        def addSelection(self,doc,obj,sub,pos):

            if self.dialog is None:
                return

            if isinstance(App.ActiveDocument.getObject(obj).Shape.getElement(sub), Part.Face):
                Gui.Selection.clearSelection
                return

            self.dialog.lbl_edge.setText(obj+'.'+sub)

            edge = App.ActiveDocument.getObject(obj)
            self.dialog.setEnd(edge.Shape.getElement(sub).Length)
            self.dialog.updateSweep()
            self.dialog.parent.recompute()

    def __init__(self, parent):
        super(SweepPicker, self).__init__()
        self.parent = parent
        self.createCallback = None
        self.destroyCallback = None
        self.hasUpdated = False
        self.current_name = "Cell"
        self.initUI()

    def _get_sketch_list(self):

        result  = ["None"]

        for obj in App.ActiveDocument.Objects:
            if type(obj).__name__=='SketchObject':
                result.append(obj.Label + " (" + obj.Name + ")")

        return result

    def updateSweep(self):

        if self.hasUpdated:
            self.destroyCallback(self.current_name)

        edge_names = self.lbl_edge.text().split('.')

        while len(edge_names) < 2:
            edge_names.append('')

        self.current_name = self.txt_name.text()
        sketch_names = self.cbo_sketch.currentText().split(' (')

        sketch_name = sketch_names[0]
        if len(sketch_names) == 2:
            sketch_name = sketch_names[1].split(')')[0]

        names = {
            "cell": self.current_name,
            "sketch": sketch_name,
            "edge_obj": edge_names[0],
            "edge": edge_names[1]
        }

        data = {
            "start": float(self.spb_start_sta.text()),
            "end": float(self.spb_end_sta.text()),
            "resolution": float(self.spb_resolution.text())
        }

        result = self.createCallback(names, data)

        if result is None:
            return

        elif not self.hasUpdated:
            self.hasUpdated = True

        self.current_name = result.Name
        self.txt_name.setText(result.Name)
        self.parent.recompute()

    def onCancel(self):
        self.destroyCallback(self.txt_name.text())
        self.close()

    def onOk(self):
        self.result = userOk
        self.close()

    def onWidgetUpdate(self, val = None):
        self.updateSweep()

    def closeEvent(self, event):

        event.accept()
        Gui.Selection.removeObserver(self.observer)

        if self.result == userCancelled:
            self.destroyCallback(self.txt_name.text())

    def setEnd(self, value):
        self.spb_end_sta.setText(str(value))

    def initUI(self):

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(250, 250, 270, 310)
        self.setWindowTitle("Our Example Nonmodal Program Window")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setMouseTracking(True)

        self.result = userCancelled

        #create cell name widgets
        self.name_label = QtGui.QLabel("Cell Name:", self)
        self.name_label.move(20, 20)

        self.txt_name = QtGui.QLineEdit("Cell", self)
        self.txt_name.setFixedWidth(100)
        self.txt_name.move(150, 20)
        self.txt_name.editingFinished.connect(self.onWidgetUpdate)

        #create template sketch picker widgets
        self.label1 = QtGui.QLabel("Template sketch:", self)
        self.label1.move(20, 60)

        sketch_list = self._get_sketch_list()

        self.cbo_sketch = QtGui.QComboBox(self)
        self.cbo_sketch.addItems(sketch_list)
        self.cbo_sketch.activated[str].connect(self.onWidgetUpdate)
        self.cbo_sketch.move(150, 60)

        #create sweep edge picker widgets
        self.label2 = QtGui.QLabel("Sweep edge:", self)
        self.label2.move(20, 100)

        self.lbl_edge = QtGui.QLabel("", self)
        self.lbl_edge.setText("")
        self.lbl_edge.setFixedWidth(280)
        self.lbl_edge.move(150, 100)

        #create line edits for start / end stations and resolution
        self.lbl_start_sta = QtGui.QLabel("Start station", self)
        self.lbl_start_sta.move(20, 140)

        self.spb_start_sta = QtGui.QLineEdit(self)
        self.spb_start_sta.setText("0.00")
        self.spb_start_sta.move(150, 140)
        self.spb_start_sta.editingFinished.connect(self.onWidgetUpdate)

        self.lbl_end_sta = QtGui.QLabel("End station", self)
        self.lbl_end_sta.move(20, 180)
        
        self.spb_end_sta = QtGui.QLineEdit(self)
        self.spb_end_sta.setText("0.00")
        self.spb_end_sta.move(150, 180)
        self.spb_end_sta.editingFinished.connect(self.onWidgetUpdate)

        self.lbl_resolution = QtGui.QLabel("Resolution", self)
        self.lbl_resolution.move(20, 220)
        
        self.spb_resolution = QtGui.QLineEdit(self)
        self.spb_resolution.setText("0.00")
        self.spb_resolution.move(150, 220)
        self.spb_resolution.editingFinished.connect(self.onWidgetUpdate)

        #cancel button
        self.cancelButton = QtGui.QPushButton('Cancel', self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.cancelButton.setFixedWidth(60)
        self.cancelButton.move(120, 270)

        #ok button
        self.okButton = QtGui.QPushButton('Ok', self)
        self.okButton.clicked.connect(self.onOk)
        self.okButton.setFixedWidth(60)
        self.okButton.move(190, 270)

        self.observer = self.SelectionObserver()
        self.observer.dialog = self

        Gui.Selection.addObserver(self.observer)

        self.show()

    def setObject(self, obj):

        if type(obj.Object).__name__ == 'SketchObject':
            if not obj.HasSubObjects:
                self.dialog.txtSketch = obj.Name
            else:
                self.dialog.txtEdge = obj.SubObjects[0].Name
        
        elif obj.HasSubObjects:
            self.dialog.txtEdge = obj.SubObjects[0]

    def findObjects(self):

        for obj in Gui.Selection.getSelectionEx():
            self.setObject(obj)