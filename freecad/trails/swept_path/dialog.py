'''simulation of traffic
swept pathes, traffic flow, traffic simulator etc. 
'''

import transportationwb
reload (transportationwb)

print "Transportation WB ",transportationwb.date," Version ", transportationwb.version

print "vehicle version  0.0" 



def createVehicle(model='generic'):
	'''creates a car'''
	print "Not yet implemented"
#	return 1
	raise Exception ("Not yet implemented")



def createTrailer(truck=None,model='generic'):
	'''creates a Trailer for a selected truck'''
	raise Exception ("Not yet implemented")





#-------------


import  transportationwb
import  transportationwb.miki_g
reload(transportationwb.miki_g)

from transportationwb.miki_g import createMikiGui, Controller


class VehicleController(Controller):


	def run(self):
		'''example button clicked method'''
		print "Button clicked"
		print self.root
		print self.root.widget


	def itemClicked(self, item):
		'''example for item clicked'''
		print item
		print item.text()




def createVehicle(model='generic'):



	layout = '''#MainWindow:
VerticalLayoutTab:

	QtGui.QLabel:
		setStyleSheet: "QWidget { font: bold 32px;color:brown;}"
		setText:"***   Configure Vehicle Demo   ***"

	QtGui.QLabel:
		setText: "Select Vehicle from Database"
	QtGui.QComboBox:
		addItem: "Truck"
		addItem: "S-Bus"
		addItem: "Bicycle"
		itemClicked.connect: app.itemClicked

	HorizontalGroup:
		setTitle: "Picture of the vehicle"
		QtGui.QLabel:
			setPixmap: QtGui.QPixmap(FreeCAD.ConfigGet('UserAppData') + '/Mod/freecad-transportation-wb/icons/vehicle_01.png')
	HorizontalGroup:
		setTitle: "Main parameters"
		QtGui.QLabel:
			setText: "B"
		QtGui.QLineEdit:
			setText:"1800"
		QtGui.QLabel:
			setText: "A"
		QtGui.QLineEdit:
			setText:"4000"
		QtGui.QLabel:
			setText: "O"
		QtGui.QLineEdit:
			setText:"1800"

		QtGui.QLabel:
			setText: "C"
		QtGui.QLineEdit:
			setText:"1800"

		QtGui.QLabel:
			setText: "Width"
		QtGui.QLineEdit:
			setText:"2500"

	HorizontalGroup:
		setTitle: "Additional parameters"
		VerticalLayout:
			HorizontalLayout:
				QtGui.QLabel:
					setText: "R"
				QtGui.QLineEdit:
					setText:"1800"
			HorizontalLayout:
				QtGui.QLabel:
					setText: "P"
				QtGui.QLineEdit:
					setText:"1800"

		VerticalLayout:
			HorizontalLayout:
				QtGui.QLabel:
					setText: "F"
				QtGui.QLineEdit:
					setText:"1800"
			HorizontalLayout:
				QtGui.QLabel:
					setText: "E"
				QtGui.QLineEdit:
					setText:"1800"

	VerticalLayout:
		HorizontalLayout:
			QtGui.QPushButton:
				setText: "Run Action"
				clicked.connect: app.run
				setIcon: QtGui.QIcon('icons:freecad.svg') 
				setIconSize: QtCore.QSize(20,20)
			QtGui.QPushButton:
				setText: "Close"
				clicked.connect: app.close
				setIcon: QtGui.QIcon('icons:edit_Cancel.svg') 
				setIconSize: QtCore.QSize(20,20)

	setSpacer:
	'''


	mikigui = createMikiGui(layout, VehicleController)
	return mikigui



#--------------


