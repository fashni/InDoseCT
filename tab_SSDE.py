from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QScrollArea, QRadioButton, QButtonGroup, QCheckBox
from PyQt5.QtCore import Qt
from tab_CTDIvol import GetMainWindowProps
from custom_widgets import HSeparator, VSeparator

class SSDETab(QWidget):
  def __init__(self, *args, **kwargs):
    super(SSDETab, self).__init__(*args, **kwargs)
    self.initVar()
    self.initUI()

  def initVar(self):
    pass

  def initUI(self):
    self.protocol = QComboBox()
    self.calc_btn = QPushButton('Calculate')

    self.ctdivol_edit = QLineEdit('0')
    self.diameter_edit = QLineEdit('0')
    self.convf_edit = QLineEdit('0')
    self.ssde_edit = QLineEdit('0')
    self.dlp_edit = QLineEdit('0')
    self.dlpc_edit = QLineEdit('0')
    self.effdose_edit = QLineEdit('0')

    grid = QGridLayout()
    grid.setHorizontalSpacing(20)
    grid.setVerticalSpacing(15)

    grid.addWidget(QLabel('CTDIVol (mGy)'), 0, 0)
    grid.addWidget(QLabel('Diameter (cm)'), 1, 0)
    grid.addWidget(QLabel('Conv Factor'), 2, 0)
    grid.addWidget(QLabel('SSDE (mGy)'), 3, 0)
    grid.addWidget(QLabel('DLP (mGy-cm)'), 0, 2)
    grid.addWidget(QLabel('DLPc (mGy-cm)'), 1, 2)
    grid.addWidget(QLabel('Effective Dose (mSv)'), 3, 2)
    grid.addWidget(self.ctdivol_edit, 0, 1)
    grid.addWidget(self.diameter_edit, 1, 1)
    grid.addWidget(self.convf_edit, 2, 1)
    grid.addWidget(self.ssde_edit, 3, 1)
    grid.addWidget(self.dlp_edit, 0, 3)
    grid.addWidget(self.dlpc_edit, 1, 3)
    grid.addWidget(self.effdose_edit, 3, 3)

    main_layout = QVBoxLayout()
    main_layout.addWidget(QLabel('Protocol:'))
    main_layout.addWidget(self.protocol)
    main_layout.addWidget(self.calc_btn)
    main_layout.addWidget(HSeparator())
    main_layout.addLayout(grid)
    main_layout.addStretch()

    self.setLayout(main_layout)

