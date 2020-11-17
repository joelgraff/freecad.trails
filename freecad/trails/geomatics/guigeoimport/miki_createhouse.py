# -------------------------------------------------
# -- createhouse, gui miki string
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
		setFixedHeight: 800
		setFixedWidth: 600
		move:  QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"B U I L D I N G LoD2 -- C O N F I G U R A T I O N"

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"D I M E N S I O N S   O F   T H E    H O U S E"
		QtGui.QLabel:


		QtGui.QLabel:
			setText:"x-dim"
		QtGui.QLineEdit:
			setText:"10000"
			id: 'le'

		QtGui.QLabel:
			setText:"y-dim"
		QtGui.QLineEdit:
			setText:"12000"
			id: 'wi'

		QtGui.QLabel:
			setText:"height block"
		QtGui.QLineEdit:
			setText:"6000"
			id: 'hiall'


		QtGui.QLabel:
			setText:"height all (block + roof)"
		QtGui.QLineEdit:
			setText:"9000"
			id: 'hi'


#		QtGui.QLabel:
#		QtGui.QLineEdit:
#			setText:"50.3736049,11.191643"
#			id: 'bl'

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"F O R M    O F   T H E    R O O F"
		QtGui.QLabel:



		QtGui.QLabel:
			setText:"midx"
		QtGui.QSlider:
			id:'midx'
			setOrientation: QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 100
			setTickInterval: 10
			setValue: 50
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QLabel:
			setText:"wx"
		QtGui.QSlider:
			id:'wx'
			setOrientation: QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 100
			setTickInterval: 10
			setValue: 50
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QLabel:
			setText:"midy"
		QtGui.QSlider:
			id:'midy'
			setOrientation: QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 100
			setTickInterval: 10
			setValue: 50
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QLabel:
			setText:"wy"
		QtGui.QSlider:
			id:'wy'
			setOrientation: QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 100
			setTickInterval: 10
			setValue: 100
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QLabel:
		QtGui.QLabel:
		QtGui.QPushButton:
			setText: "Build the house"
			clicked.connect: app.gen_house

		QtGui.QLabel:
		QtGui.QLabel:

		QtGui.QLabel:
			setText:'Position'
		QtGui.QLineEdit:
			setText:"50.3736049,11.191643"
			id: 'bl'

		QtGui.QLabel:
			setText:'Orientation'
		QtGui.QLineEdit:
			setText:"90"
			id: 'bl'


'''
