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
#VerticalLayoutTab:
MainWindow:
	VerticalLayout:
		id:'main'

		QtGui.QLabel:
			setText:"***   I M A G E   T O    N U R B S    ***"

	VerticalLayout:
		id:'img1'
#		setVisible:False

		QtGui.QPushButton:
			setText: "Browse for input data filename"
			clicked.connect: app.getfn

		QtGui.QLineEdit:
			setText:"UserAppData/Mod/geodat/testdata/freeka.png"
			id: 'bl'

		HorizontalLayout:
			QtGui.QLabel:
				setText:"Scale  "

			QtGui.QLineEdit:
				setText:"10"
				id: 'kx'

			QtGui.QLineEdit:
				setText:"10"
				id: 'ky'

			QtGui.QLineEdit:
				setText:"60"
				id: 'kz'

		QtGui.QCheckBox:
			id: 'inverse' 
			setText: 'Invert Height'
			setChecked: False

		QtGui.QLabel:
			setText:"Border Size "

		QtGui.QLineEdit:
			setText:"5"
			id: 'border'

		QtGui.QLabel:
			setText:"Color Channel RGB 012 3-grey noimp "

		QtGui.QLineEdit:
			setText:"2"
			id: 'color'

		QtGui.QCheckBox:
			id: 'pointsonly' 
			setText: 'create only a Pointcloud'
			setChecked: True


		QtGui.QCheckBox:
			id: 'gengrid' 
			setText: 'create Nurbs Grid'
			setChecked: True

		QtGui.QCheckBox:
			id: 'genblock' 
			setText: 'create Nurbsblock Solid'
			setChecked: False

		QtGui.QCheckBox:
			id: 'genpoles' 
			setText: 'create Pole Cloud'
			setChecked: False


	QtGui.QPushButton:
		setText: "import image"
		id:'run'
		clicked.connect: app.run

'''
