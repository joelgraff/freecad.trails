from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebEngineWidgets import QWebEnginePage 
from PySide2.QtCore import QUrl

#Styles PySide

StyleSheet = "QWidget {background-color: rgb(68, 68, 68)} QPushButton { background-color: black } QGroupBox {border: 1px solid grey; }"

def webViewGroup(self):
	self.webView = QWebEngineView()
	self.webPage = QWebEnginePage()
	self.webPage.load(QUrl(QtCore.QUrl(self.filepathNewMap)))
	self.webView.setObjectName("webView")
	self.webView.setPage(self.webPage)
	self.webView.show()
	
	groupBox = QtWidgets.QGroupBox("Map")
	groupBox.setStyleSheet("QGroupBox {border: 1px solid grey;}")
	vbox = QtWidgets.QVBoxLayout()
	vbox.addWidget(self.webView)
	groupBox.setLayout(vbox)

	return groupBox

def locationGroup(self):
	groupBox = QtWidgets.QGroupBox("Location / Boundingbox")
	latLonLab = QtWidgets.QLabel("lat/lon (WGS-84)")
	latLon = QtWidgets.QLabel("lat: " + self.lat + ", lon: " + self.lon)
	CRSLab = QtWidgets.QLabel("Sec. CRS")
	CRSText = QtWidgets.QLabel(self.CRS + " " + self.CRSDescription)

	xCoordLab = QtWidgets.QLabel("X-coordinate")
	xCoord = QtWidgets.QLabel(self.X)
	yCoordLab = QtWidgets.QLabel("Y-coordinate")
	yCoord = QtWidgets.QLabel(self.Y)
	bboxWidthLab = QtWidgets.QLabel("Boundingbox Width [m]")
	self.bboxWidth = QtWidgets.QLineEdit()
	self.bboxWidth.setText(self.bboxWidthStart)
	self.bboxWidth.editingFinished.connect(self.onbboxWidth)
	bboxHeightLab = QtWidgets.QLabel("Boundingbox Height [m]")
	self.bboxHeight = QtWidgets.QLineEdit()
	self.bboxHeight.setText(self.bboxHeightStart)
	self.bboxHeight.editingFinished.connect(self.onbboxHeight)	

	grid = QtWidgets.QGridLayout()
	grid.addWidget(latLonLab,0,0)
	grid.addWidget(latLon,0,1)
	grid.addWidget(CRSLab,1,0)
	grid.addWidget(CRSText,1,1)
	grid.addWidget(xCoordLab,2,0)
	grid.addWidget(xCoord,2,1)
	grid.addWidget(yCoordLab,3,0)
	grid.addWidget(yCoord,3,1)
	grid.addWidget(bboxWidthLab,4,0)
	grid.addWidget(self.bboxWidth,4,1)
	grid.addWidget(bboxHeightLab,5,0)
	grid.addWidget(self.bboxHeight,5,1)

	groupBox.setLayout(grid)
	groupBox.setStyleSheet("QGroupBox {border: 1px solid grey;}")

	return groupBox

def buttonGroup(self):
	importbtn = QtWidgets.QPushButton("Import")
	importbtn.clicked.connect(self.onImport)
	testbtn = QtWidgets.QPushButton("Test")
	testbtn.clicked.connect(self.onTest)
	cancelbtn = QtWidgets.QPushButton("Cancel")	
	cancelbtn.clicked.connect(self.onCancel)

	hbox = QtWidgets.QHBoxLayout()
	hbox.addWidget(importbtn)
	hbox.addWidget(testbtn)
	hbox.addWidget(cancelbtn)
			
	return hbox
	
def buttonGroupOKCancel(self):
	okbtn = QtWidgets.QPushButton("OK")
	okbtn.clicked.connect(self.onOk)
	cancelbtn = QtWidgets.QPushButton("Cancel")	
	cancelbtn.clicked.connect(self.onCancel)
	hbox = QtWidgets.QHBoxLayout()
	hbox.addWidget(okbtn)
	hbox.addWidget(cancelbtn)
				
	return hbox