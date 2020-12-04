from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QComboBox, QLineEdit, QPushButton, QScrollArea, QRadioButton, QGroupBox,
                             QButtonGroup, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlTableModel
import numpy as np
from custom_widgets import HSeparator
from constants import *
from db import get_records
from Plot import PlotDialog
from scipy import interpolate

class SSDETab(QWidget):
  def __init__(self, ctx, *args, **kwargs):
    super(SSDETab, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.initModel()
    self.initData()
    self.initUI()
    self.sigConnect()

  def initModel(self):
    self.protocol_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.head_ap_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.head_lat_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.head_e_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.thorax_ap_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.thorax_lat_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.thorax_e_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.effdose_model = QSqlTableModel(db=self.ctx.database.ssde_db)

    self.protocol_model.setTable("Protocol")
    self.head_ap_model.setTable("HeadAP")
    self.head_lat_model.setTable("HeadLAT")
    self.head_e_model.setTable("HeadE")
    self.thorax_ap_model.setTable("ThoraxAP")
    self.thorax_lat_model.setTable("ThoraxLAT")
    self.thorax_e_model.setTable("ThoraxE")
    self.effdose_model.setTable("Effective_Dose")

    self.protocol_model.setFilter("Group_ID=1")

    self.protocol_model.select()
    self.head_ap_model.select()
    self.head_lat_model.select()
    self.head_e_model.select()
    self.thorax_ap_model.select()
    self.thorax_lat_model.select()
    self.thorax_e_model.select()
    self.effdose_model.select()

  def getData(self, model):
    data = [[model.data(model.index(i,j)) for i in range(model.rowCount())] for j in range(1,3)]
    return np.array(data).T

  def initData(self):
    self.head_ap_data = self.getData(self.head_ap_model)
    self.head_lat_data = self.getData(self.head_lat_model)
    self.head_e_data = self.getData(self.head_e_model)
    self.thorax_ap_data = self.getData(self.thorax_ap_model)
    self.thorax_lat_data = self.getData(self.thorax_lat_model)
    self.thorax_e_data = self.getData(self.thorax_e_model)

    self.head_ap_interp = interpolate.splrep(self.head_ap_data[:,0], self.head_ap_data[:,1])
    self.head_lat_interp = interpolate.splrep(self.head_lat_data[:,0], self.head_lat_data[:,1])
    self.head_e_interp = interpolate.splrep(self.head_e_data[:,0], self.head_e_data[:,1])
    self.thorax_ap_interp = interpolate.splrep(self.thorax_ap_data[:,0], self.thorax_ap_data[:,1])
    self.thorax_lat_interp = interpolate.splrep(self.thorax_lat_data[:,0], self.thorax_lat_data[:,1])
    self.thorax_e_interp = interpolate.splrep(self.thorax_e_data[:,0], self.thorax_e_data[:,1])

  def initUI(self):
    self.protocol = QComboBox()
    self.protocol.setModel(self.protocol_model)
    self.protocol.setModelColumn(self.protocol_model.fieldIndex('name'))
    self.calc_btn = QPushButton('Calculate')
    self.plot_btn = QPushButton('Plot Result')
    self.save_btn = QPushButton('Save')
    self.plot_btn.setEnabled(False)
    self.plot_btn.setVisible(False)

    self.diameter_label = QLabel('<b>Diameter (cm)</b>')
    self.ctdiv_edit = QLineEdit(f'{self.ctx.app_data.CTDIv}')
    self.diameter_edit = QLineEdit(f'{self.ctx.app_data.diameter}')
    self.convf_edit = QLineEdit(f'{self.ctx.app_data.convf}')
    self.ssde_edit = QLineEdit(f'{self.ctx.app_data.SSDE}')
    self.dlp_edit = QLineEdit(f'{self.ctx.app_data.DLP}')
    self.dlpc_edit = QLineEdit(f'{self.ctx.app_data.DLPc}')
    self.effdose_edit = QLineEdit(f'{self.ctx.app_data.effdose}')

    self.diameter_mode_handle(DEFF_IMAGE)

    self.next_tab_btn = QPushButton('Next')
    self.prev_tab_btn = QPushButton('Previous')
    self.next_tab_btn.setVisible(False)

    edits = [
      self.ctdiv_edit,
      self.diameter_edit,
      self.convf_edit,
      self.ssde_edit,
      self.dlp_edit,
      self.dlpc_edit,
      self.effdose_edit,
    ]

    [edit.setReadOnly(True) for edit in edits]
    [edit.setAlignment(Qt.AlignRight) for edit in edits]

    left_grpbox = QGroupBox()
    left_layout = QFormLayout()
    left_layout.addRow(QLabel('<b>CTDIvol (mGy)</b>'), self.ctdiv_edit)
    left_layout.addRow(self.diameter_label, self.diameter_edit)
    left_layout.addRow(QLabel('<b>Conv Factor</b>'), self.convf_edit)
    left_layout.addRow(QLabel('<b>SSDE (mGy)</b>'), self.ssde_edit)
    left_grpbox.setLayout(left_layout)

    right_grpbox = QGroupBox()
    right_layout = QFormLayout()
    right_layout.addRow(QLabel('<b>DLP (mGy-cm)</b>'), self.dlp_edit)
    right_layout.addRow(QLabel('<b>DLP<sub>c</sub> (mGy-cm)</b>'), self.dlpc_edit)
    right_layout.addRow(QLabel(''))
    right_layout.addRow(QLabel('<b>Effective Dose (mSv)</b>'), self.effdose_edit)
    right_grpbox.setLayout(right_layout)

    h = QHBoxLayout()
    h.addWidget(left_grpbox)
    h.addWidget(right_grpbox)

    tab_nav = QHBoxLayout()
    tab_nav.addWidget(self.prev_tab_btn)
    tab_nav.addStretch()
    tab_nav.addWidget(self.next_tab_btn)

    main_layout = QVBoxLayout()
    main_layout.addWidget(QLabel('Protocol:'))
    main_layout.addWidget(self.protocol)
    main_layout.addWidget(HSeparator())
    main_layout.addLayout(h)
    main_layout.addWidget(self.calc_btn)
    main_layout.addWidget(self.plot_btn)
    main_layout.addWidget(self.save_btn)
    main_layout.addStretch()
    main_layout.addLayout(tab_nav)

    self.setLayout(main_layout)

  def sigConnect(self):
    self.protocol.activated[int].connect(self.on_protocol_changed)
    self.calc_btn.clicked.connect(self.on_calculate)
    self.ctx.app_data.modeValueChanged.connect(self.diameter_mode_handle)
    self.ctx.app_data.diameterValueChanged.connect(self.diameter_handle)
    self.ctx.app_data.CTDIValueChanged.connect(self.ctdiv_handle)
    self.ctx.app_data.DLPValueChanged.connect(self.dlp_handle)
    self.plot_btn.clicked.connect(self.on_plot)

  def plot(self, data):
    x = self.ctx.app_data.diameter
    y = self.ctx.app_data.convf
    xlabel = 'Dw' if self.ctx.app_data.mode==DW else 'Deff'
    title = 'Water Equivalent Diameter' if self.ctx.app_data.mode==DW else 'Effective Diameter'
    self.figure = PlotDialog()
    self.figure.actionEnabled(True)
    self.figure.plot(data, pen={'color': "FFFF00", 'width': 2}, symbol=None)
    self.figure.scatter([x], [y], symbol='o', symbolPen=None, symbolSize=8, symbolBrush=(255, 0, 0, 255))
    self.figure.annotate(pos=(x,y), text=f'{xlabel}: {x:#.2f} cm\nConv. Factor: {y:#.2f}', anchor=(0,1))
    self.figure.axes.showGrid(True,True)
    self.figure.setLabels(xlabel,'Conversion Factor','cm',None)
    self.figure.setTitle(f'{title} - Conversion Factor')
    self.figure.show()

  def diameter_mode_handle(self, value):
    if value == DW:
      self.diameter_label.setText('<b>Dw (cm)</b>')
    else:
      self.diameter_label.setText('<b>Deff (cm)</b>')

  def diameter_handle(self, value):
    self.diameter_edit.setText(f'{value:#.4f}')

  def ctdiv_handle(self, value):
    self.ctdiv_edit.setText(f'{value:#.4f}')

  def dlp_handle(self, value):
    self.dlp_edit.setText(f'{value:#.4f}')

  def on_protocol_changed(self, idx):
    self.protocol_id = self.protocol_model.record(idx).value("id")
    self.alfa = self.effdose_model.record(self.protocol_id-1).value("alfaE")
    self.beta = self.effdose_model.record(self.protocol_id-1).value("betaE")
    print(self.protocol_id, self.alfa, self.beta)

  def on_calculate(self):
    if self.ctx.app_data.mode == DEFF_AP:
      self.data = self.head_ap_data if self.ctx.phantom == HEAD else self.thorax_ap_data
      interp = self.head_ap_interp if self.ctx.phantom == HEAD else self.thorax_ap_interp
    elif self.ctx.app_data.mode == DEFF_LAT:
      self.data = self.head_lat_data if self.ctx.phantom == HEAD else self.thorax_lat_data
      interp = self.head_lat_interp if self.ctx.phantom == HEAD else self.thorax_lat_interp
    else:
      self.data = self.head_e_data if self.ctx.phantom == HEAD else self.thorax_e_data
      interp = self.head_e_interp if self.ctx.phantom == HEAD else self.thorax_e_interp

    self.ctx.app_data.convf = float(interpolate.splev(self.ctx.app_data.diameter, interp))
    self.ctx.app_data.SSDE = self.ctx.app_data.convf * self.ctx.app_data.CTDIv
    self.ctx.app_data.DLPc = self.ctx.app_data.convf * self.ctx.app_data.DLP
    self.ctx.app_data.effdose = self.ctx.app_data.DLP * np.exp(self.alfa*self.ctx.app_data.diameter + self.beta)

    self.convf_edit.setText(f'{self.ctx.app_data.convf:#.4f}')
    self.ssde_edit.setText(f'{self.ctx.app_data.SSDE:#.4f}')
    self.dlpc_edit.setText(f'{self.ctx.app_data.DLPc:#.4f}')
    self.effdose_edit.setText(f'{self.ctx.app_data.effdose:#.4f}')
    self.plot_btn.setEnabled(True)
    self.on_plot()

  def on_plot(self):
    self.plot(self.data)

  def reset_fields(self):
    self.protocol.setCurrentIndex(0)
    self.on_protocol_changed(0)
    self.plot_btn.setEnabled(False)
    self.ctdiv_edit.setText(f'{self.ctx.app_data.CTDIv}')
    self.diameter_edit.setText(f'{self.ctx.app_data.diameter}')
    self.convf_edit.setText(f'{self.ctx.app_data.convf}')
    self.ssde_edit.setText(f'{self.ctx.app_data.SSDE}')
    self.dlp_edit.setText(f'{self.ctx.app_data.DLP}')
    self.dlpc_edit.setText(f'{self.ctx.app_data.DLPc}')
    self.effdose_edit.setText(f'{self.ctx.app_data.effdose}')
