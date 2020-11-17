# -------------------------------------------------
# -- xzy importer, gui miki string
# --
# -- microelly 2016 v 0.4
# -- Bernd Hahnebach <bernd@bimstatik.org> 2020
# --
# -- GNU Lesser General Public License (LGPL)
# -------------------------------------------------
"""the dialog layout as miki string"""

 
sdialog = '''
#VerticalLayoutTab:
MainWindow:
	VerticalLayout:
		id:'main'


		QtGui.QLabel:
			setText:"***   I M P O R T    Data from xyz   ***"

		QtGui.QCheckBox:
			id: 'pclMode' 
			setText: 'Use existing Point Cloud'
			stateChanged.connect: app.pclMode
			setChecked: True


	VerticalLayout:
		id:'img1'
		setVisible:False

		QtGui.QPushButton:
			setText: "Browse for input data filename"
			clicked.connect: app.getfn

		QtGui.QLineEdit:
#			setText:"/home/microelly2/FCB/b202_gmx_tracks/dgm1/dgm1_32356_5638_2_nw.xyz"
			setText:"/home/thomas/Dokumente/freecad_buch/b202_gmx_tracks/dgm1/dgm1_32356_5638_2_nw.xyz"
			setText:"UserAppData/Mod/geodat/testdata/xyz.txt"
			id: 'bl'

		HorizontalLayout:
			QtGui.QLabel:
				setText:"Reduction Factor  "

			QtGui.QLineEdit:
				setText:"10"
				setText:"1"
				id: 'ku'

			QtGui.QLineEdit:
				setText:"10"
				setText:"1"
				id: 'kv'


	VerticalLayout:
		id:'img2'

		QtGui.QLabel:
			setText:"Point Cloud Name"

		QtGui.QLineEdit:
			setText:"Points 110 99"
			setText:"Points"
			id: 'pclLabel'


		HorizontalLayout:
			QtGui.QLabel:
				setText:"Size lu,lv  "

		QtGui.QLineEdit:
			setText:"3"
			#setText:"110"
			id: 'lu'

		QtGui.QLineEdit:
			setText:"3"
			#setText:"99"
			id: 'lv'


	QtGui.QPushButton:
		setText: "initialize values"
		id:'run'
		clicked.connect: app.run



	VerticalLayout:
		id:'post'
		setVisible: False

		QtGui.QLabel:
			setText:"Create Nurbs Surfaces inside a Rectangle"

		HorizontalLayout:

			QtGui.QLabel:
				setText:"Frame position"

			QtGui.QDial:
				setValue: 0
				id: 'ud'
				setMinimum: 0
				setMaximum: 200
				setTickInterval: 1
				valueChanged.connect: app.showFrame


			QtGui.QDial:
				setValue: 0
				id: 'vd'
				setMinimum: 0
				setMaximum: 200
				setTickInterval: 1
				valueChanged.connect: app.showFrame
				valueChanged.connect: app.update2

		HorizontalLayout:

			QtGui.QLabel:
				setText:"Frame size"
				valueChanged.connect: app.showFrame
#				valueChanged.connect: app.update2

			QtGui.QDial:
				setValue: 5
				id: 'dd'
				setMinimum: 1
				setMaximum: 100
				setTickInterval: 1
				valueChanged.connect: app.update2
#				valueChanged.connect: app.showFrame

		HorizontalLayout:
			QtGui.QPushButton:
				setText: "hide Frame"
				clicked.connect: app.hideFrame

			QtGui.QPushButton:
				setText: "create Nurbs"
				clicked.connect: app.createNurbs

			QtGui.QPushButton:
				setText: "create Mesh"
				clicked.connect: app.createMesh


'''
