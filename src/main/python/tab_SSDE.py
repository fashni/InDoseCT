from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QScrollArea, QRadioButton, QButtonGroup, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import numpy as np
from custom_widgets import HSeparator, VSeparator
from constants import *
from db import get_records
from scipy import interpolate

class SSDETab(QWidget):
  def __init__(self, ctx, *args, **kwargs):
    super(SSDETab, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.initDB()
    self.initModel()
    self.initData()
    self.initUI()
    self.sigConnect()

  def initDB(self):
    self.db = QSqlDatabase.addDatabase("QSQLITE", "SSDEConnection")
    self.db.setDatabaseName(self.ctx.ssde_db)
    if not self.db.open():
      QMessageBox.warning(None, f"Database Error: {self.db.lastError().text()}")

  def initModel(self):
    self.query_model = QSqlQueryModel()
    self.head_ap_model = QSqlTableModel(db=self.db)
    self.head_lat_model = QSqlTableModel(db=self.db)
    self.head_e_model = QSqlTableModel(db=self.db)
    self.thorax_ap_model = QSqlTableModel(db=self.db)
    self.thorax_lat_model = QSqlTableModel(db=self.db)
    self.thorax_e_model = QSqlTableModel(db=self.db)
    self.head_ap_model.setTable("HeadAP")
    self.head_lat_model.setTable("HeadLAT")
    self.head_e_model.setTable("HeadE")
    self.thorax_ap_model.setTable("ThoraxAP")
    self.thorax_lat_model.setTable("ThoraxLAT")
    self.thorax_e_model.setTable("ThoraxE")

    self.head_ap_model.select()
    self.head_lat_model.select()
    self.head_e_model.select()
    self.thorax_ap_model.select()
    self.thorax_lat_model.select()
    self.thorax_e_model.select()

  def initData(self):
    data = [[self.head_ap_model.data(self.head_ap_model.index(i,j))
             for i in range(self.head_ap_model.rowCount())] for j in range(1,3)]
    self.head_ap_data = np.array(data).T
    self.head_ap_interp = interpolate.splrep(self.head_ap_data[:,0], self.head_ap_data[:,1])

    data = [[self.head_lat_model.data(self.head_lat_model.index(i,j))
             for i in range(self.head_lat_model.rowCount())] for j in range(1,3)]
    self.head_lat_data = np.array(data).T
    self.head_lat_interp = interpolate.splrep(self.head_lat_data[:,0], self.head_lat_data[:,1])

    data = [[self.head_e_model.data(self.head_e_model.index(i,j))
             for i in range(self.head_e_model.rowCount())] for j in range(1,3)]
    self.head_e_data = np.array(data).T
    self.head_e_interp = interpolate.splrep(self.head_e_data[:,0], self.head_e_data[:,1])

    data = [[self.thorax_ap_model.data(self.thorax_ap_model.index(i,j))
             for i in range(self.thorax_ap_model.rowCount())] for j in range(1,3)]
    self.thorax_ap_data = np.array(data).T
    self.thorax_ap_interp = interpolate.splrep(self.thorax_ap_data[:,0], self.thorax_ap_data[:,1])

    data = [[self.thorax_lat_model.data(self.thorax_lat_model.index(i,j))
             for i in range(self.thorax_lat_model.rowCount())] for j in range(1,3)]
    self.thorax_lat_data = np.array(data).T
    self.thorax_lat_interp = interpolate.splrep(self.thorax_lat_data[:,0], self.thorax_lat_data[:,1])

    data = [[self.thorax_e_model.data(self.thorax_e_model.index(i,j))
             for i in range(self.thorax_e_model.rowCount())] for j in range(1,3)]
    self.thorax_e_data = np.array(data).T
    self.thorax_e_interp = interpolate.splrep(self.thorax_e_data[:,0], self.thorax_e_data[:,1])

  def initUI(self):
    self.protocol = QComboBox()
    self.protocol.addItems(HEAD_PROTOCOL)
    self.on_protocol_changed(HEAD_PROTOCOL[0])
    self.calc_btn = QPushButton('Calculate')
    self.save_btn = QPushButton('Save')

    self.ctdiv_edit = QLineEdit(f'{self.ctx.app_data.CTDIv}')
    self.diameter_edit = QLineEdit(f'{self.ctx.app_data.diameter}')
    self.convf_edit = QLineEdit(f'{self.ctx.app_data.convf}')
    self.ssde_edit = QLineEdit(f'{self.ctx.app_data.SSDE}')
    self.dlp_edit = QLineEdit(f'{self.ctx.app_data.DLP}')
    self.dlpc_edit = QLineEdit(f'{self.ctx.app_data.DLPc}')
    self.effdose_edit = QLineEdit(f'{self.ctx.app_data.effdose}')

    self.diameter_label = QLabel('Diameter (cm)')

    grid = QGridLayout()
    grid.setHorizontalSpacing(20)
    grid.setVerticalSpacing(15)

    grid.addWidget(QLabel('CTDIvol (mGy)'), 0, 0)
    grid.addWidget(self.diameter_label, 1, 0)
    grid.addWidget(QLabel('Conv Factor'), 2, 0)
    grid.addWidget(QLabel('SSDE (mGy)'), 3, 0)
    grid.addWidget(QLabel('DLP (mGy-cm)'), 0, 2)
    grid.addWidget(QLabel('DLPc (mGy-cm)'), 1, 2)
    grid.addWidget(QLabel('Effective Dose (mSv)'), 3, 2)
    grid.addWidget(self.ctdiv_edit, 0, 1)
    grid.addWidget(self.diameter_edit, 1, 1)
    grid.addWidget(self.convf_edit, 2, 1)
    grid.addWidget(self.ssde_edit, 3, 1)
    grid.addWidget(self.dlp_edit, 0, 3)
    grid.addWidget(self.dlpc_edit, 1, 3)
    grid.addWidget(self.effdose_edit, 3, 3)

    h = QHBoxLayout()
    h.addWidget(self.save_btn)
    h.addStretch()

    main_layout = QVBoxLayout()
    main_layout.addWidget(QLabel('Protocol:'))
    main_layout.addWidget(self.protocol)
    main_layout.addWidget(self.calc_btn)
    main_layout.addWidget(HSeparator())
    main_layout.addLayout(grid)
    main_layout.addStretch()
    main_layout.addLayout(h)
    main_layout.addStretch()

    self.setLayout(main_layout)

  def sigConnect(self):
    self.protocol.activated[str].connect(self.on_protocol_changed)
    self.calc_btn.clicked.connect(self.on_calculate)
    self.ctx.app_data.modeValueChanged.connect(self.diameter_mode_handle)
    self.ctx.app_data.diameterValueChanged.connect(self.diameter_handle)
    self.ctx.app_data.CTDIValueChanged.connect(self.ctdiv_handle)
    self.ctx.app_data.DLPValueChanged.connect(self.dlp_handle)

  def plot(self):
    pass

  def diameter_mode_handle(self, value):
    if value == DW:
      self.diameter_label.setText('Dw (cm)')
    else:
      self.diameter_label.setText('Deff (cm)')

  def diameter_handle(self, value):
    self.diameter_edit.setText(f'{value:#.4f}')

  def ctdiv_handle(self, value):
    self.ctdiv_edit.setText(f'{value:#.4f}')

  def dlp_handle(self, value):
    self.dlp_edit.setText(f'{value:#.4f}')

  def on_protocol_changed(self, text):
    sql = f'SELECT alfaE, betaE FROM Effective_Dose WHERE Protocol="{text}"'
    self.query_model.setQuery(sql, self.db)
    self.alfa = self.query_model.record(0).value('alfaE')
    self.beta = self.query_model.record(0).value('betaE')

  def on_calculate(self):
    if self.ctx.app_data.mode == DEFF_AP:
      data = self.head_ap_data if self.ctx.phantom == HEAD else self.thorax_ap_data
      interp = self.head_ap_interp if self.ctx.phantom == HEAD else self.thorax_ap_interp
    elif self.ctx.app_data.mode == DEFF_LAT:
      data = self.head_lat_data if self.ctx.phantom == HEAD else self.thorax_lat_data
      interp = self.head_lat_interp if self.ctx.phantom == HEAD else self.thorax_lat_interp
    else:
      data = self.head_e_data if self.ctx.phantom == HEAD else self.thorax_e_data
      interp = self.head_e_interp if self.ctx.phantom == HEAD else self.thorax_e_interp

    self.ctx.app_data.convf = float(interpolate.splev(self.ctx.app_data.diameter, interp))
    self.ctx.app_data.SSDE = self.ctx.app_data.convf * self.ctx.app_data.CTDIv
    self.ctx.app_data.DLPc = self.ctx.app_data.convf * self.ctx.app_data.DLP
    self.ctx.app_data.effdose = self.ctx.app_data.DLP * np.exp(self.alfa*self.ctx.app_data.diameter + self.beta)

    self.convf_edit.setText(f'{self.ctx.app_data.convf:#.4f}')
    self.ssde_edit.setText(f'{self.ctx.app_data.SSDE:#.4f}')
    self.dlpc_edit.setText(f'{self.ctx.app_data.DLPc:#.4f}')
    self.effdose_edit.setText(f'{self.ctx.app_data.effdose:#.4f}')
