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


		QtGui.QLabel:
			setText:"***   I M P O R T    L I D A R   ***"

		QtGui.QCheckBox:
			id: 'createPCL' 
			setText: 'create Point Cloud'
#			stateChanged.connect: app.pclMode
			setChecked: True

		QtGui.QCheckBox:
			id: 'useOrigin' 
			setText: 'use Origin of Data'
#			stateChanged.connect: app.pclMode
#			setChecked: True

		QtGui.QPushButton:
			setText: "Browse for input data filename."
			clicked.connect: app.getfn

		QtGui.QLineEdit:
			setText:"/media/thomas/b08575a9-0252-47ca-971e-f94c20b33801/geodat_DATEN/las_lee_county/24561900.las"
			id: 'bl'

	QtGui.QPushButton:
		setText: "initialize values"
		id:'run'
		clicked.connect: app.run

'''
