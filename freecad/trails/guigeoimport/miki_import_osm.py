# -------------------------------------------------
# -- osm map importer, gui miki string
# --
# -- microelly 2016 v 0.4
# -- Bernd Hahnebach <bernd@bimstatik.org> 2020
# --
# -- GNU Lesser General Public License (LGPL)
# -------------------------------------------------
"""the dialog layout as miki string"""

 
s6 = '''
#VerticalLayoutTab:
MainWindow:
#DockWidget:
	VerticalLayout:
		id:'main'
		setFixedHeight: 600
		setFixedWidth: 730
		setFixedWidth: 654
		move:  QtCore.QPoint(3000,100)


		HorizontalLayout:
			setFixedHeight: 50
			QtGui.QLabel:
				setFixedWidth: 600

		QtGui.QLabel:
			setText:"C o n f i g u r a t i o n s"
			setFixedHeight: 20
		QtGui.QLineEdit:
			setText:"50.340722, 11.232647"
#			setText:"50.3736049,11.191643"
#			setText:"50.3377879,11.2104096"
			id: 'bl'
			setFixedHeight: 20
			textChanged.connect: app.getSeparator
		QtGui.QLabel:
		QtGui.QLabel:
			setText:"S e p a r a t o r"
			setFixedHeight: 20
		QtGui.QLineEdit:
			id:'sep'
			setPlaceholderText:"Enter separators separated by symbol: |   example: @|,|:"
			setToolTip:"<nobr>Enter separators separated by symbol: |</nobr><br>example: @|,|:"
			setFixedHeight: 20

		QtGui.QPushButton:
			setText:"Help"
			setFixedHeight: 20
			clicked.connect: app.showHelpBox

		QtGui.QLabel:
		QtGui.QPushButton:
			setText:"Get Coordinates "
			setFixedHeight: 20
			clicked.connect: app.getCoordinate



		QtGui.QLabel:	
		HorizontalLayout:
			setFixedHeight: 50
			QtGui.QLabel:
				setFixedWidth: 150
			QtGui.QLineEdit:
				id:'lat'
				setText:"50.340722"
				setFixedWidth: 100
			QtGui.QPushButton:
				id:'swap'
				setText:"swap"
				setFixedWidth: 50
				clicked.connect: app.swap
			QtGui.QLineEdit:
				id:'long'
				setText:"11.232647"
				setFixedWidth: 100
		
		HorizontalLayout:
			setFixedHeight: 50
			QtGui.QLabel:
				setFixedWidth: 155
			QtGui.QLabel:
				setText:"Latitude"
				setFixedWidth: 100
			QtGui.QLabel:
				setFixedWidth: 50
			QtGui.QLabel:
				setText:"Longitude"
				setFixedWidth: 100

		QtGui.QLabel:
		QtGui.QLabel:
		QtGui.QCheckBox:
			id:'elevation'
			setText: 'Process Elevation Data'

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"Length of the Square 0 km ... 4 km, default 0.5 km  "

		QtGui.QLabel:
			setText:"Distance is 0.5 km."
			id: "showDistanceLabel"
		QtGui.QSlider:
			id:'s'
			setFixedHeight: 20
			setOrientation: QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 40
			setTickInterval: 1
			setValue: 5
			setTickPosition: QtGui.QSlider.TicksBothSides
			valueChanged.connect: app.showDistanceOnLabel

		QtGui.QLabel:
		QtGui.QLabel:
			id:'running'
			setText:"R u n n i n g   Please Wait  "
			setVisible: False

		QtGui.QPushButton:
			id:'runbl1'
			setText: "Download values"
			setFixedHeight: 20
			clicked.connect: app.downloadData
			setVisible: True

		QtGui.QPushButton:
			id:'runbl2'
			setText: "Apply values"
			setFixedHeight: 20
			clicked.connect: app.applyData
			setVisible: False


		QtGui.QPushButton:
			setText: "Show openstreet map in web browser"
			clicked.connect: app.showMap
			setFixedHeight: 20

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"P r e d e f i n e d   L o c a t i o n s"
#		QtGui.QLabel:

		QtGui.QRadioButton:
			setText: "Sonneberg Outdoor Inn"
			clicked.connect: app.run_sternwarte

		QtGui.QRadioButton:
			setText: "Coburg university and school "
			clicked.connect: app.run_co2

		QtGui.QRadioButton:
			setText: "Berlin Alexanderplatz/Haus des Lehrers"
			clicked.connect: app.run_alex

		QtGui.QRadioButton:
			setText: "Berlin Spandau"
			clicked.connect: app.run_spandau

		QtGui.QRadioButton:
			setText: "Paris Rue de Seine"
			clicked.connect: app.run_paris

		QtGui.QRadioButton:
			setText: "Tokyo near tower"
			clicked.connect: app.run_tokyo

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"P r o c e s s i n g:"
			id: "status"
			setFixedHeight: 20

		QtGui.QLabel:
			setText:"---"
			id: "status"
		QtGui.QProgressBar:
			id: "progb"
			setFixedHeight: 20

'''
