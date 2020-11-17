# -------------------------------------------------
# -- srtm importer, gui miki string
# --
# -- microelly 2016 v 0.4
# -- Bernd Hahnebach <bernd@bimstatik.org> 2020
# --
# -- GNU Lesser General Public License (LGPL)
# -------------------------------------------------
"""the dialog layout as miki string"""

 
sdialog = '''
MainWindow:
	VerticalLayout:
		id:'main'
#		setFixedHeight: 600
		setFixedWidth: 250
		move:  QtCore.QPoint(100,100)

		QtGui.QLabel:
			setText:"I m p o r t    S R T M   Elevations"

		QtGui.QLabel:
			setText:"Location:"


		QtGui.QLineEdit:
			setText:"45.7750419,2.902975"
#			setText:"50.3736049,11.191643"
			id: 'bl'

		QtGui.QLabel:
			setText:"Area Interval:"
			
		QtGui.QLineEdit:
			setText:"0.03,0.03"
			id: 'dbl'

		QtGui.QPushButton:
			setText: "Create Elevation Points"
			clicked.connect: app.runbl

		QtGui.QPushButton:
			setText: "Show in OpenStreetMap"
			clicked.connect: app.run_browser

		QtGui.QPushButton:
			setText: "Show in Google Maps"
			clicked.connect: app.run_google

		QtGui.QPushButton:
			setText: "Reit und Wanderkarte"
			clicked.connect: app.run_reitwander


		QtGui.QLabel:
			setText:"Test Case Coords ..."

		QtGui.QPushButton:
			setText: "Nizza"
			clicked.connect: app.run_nizza

		QtGui.QPushButton:
			setText: "Puy de Dome"
			clicked.connect: app.run_puydedome

		QtGui.QPushButton:
			setText: "Mount Everest"
			clicked.connect: app.run_everest

		QtGui.QPushButton:
			setText: "Outdoor Inn"
			clicked.connect: app.run_outdoorinn




'''
