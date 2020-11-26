from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QFormLayout, QStackedLayout, QLineEdit, QPushButton,
                             QLabel, QWidget, QComboBox, QMessageBox, QGroupBox)
from PyQt5.QtSql import QSqlTableModel
from custom_widgets import HSeparator, VSeparator
from constants import *
from Plot import PlotDialog

class CTDIVolTab(QWidget):
  def __init__(self, ctx, *args, **kwargs):
    super(CTDIVolTab, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.initVar()
    self.initModel()
    self.initUI()
    self.setModel()
    self.sigConnect()
    self.calculate()

  def initVar(self):
    self.prev_mode = 0
    self.mode = 0
    self.CTDI = 0
    self.DLP = 0
    self.tube_current = 100
    self.rotation_time = 1
    self.pitch = 1
    self.coll = 0
    self.scan_length = 10
    self.mAs = 0
    self.eff_mAs = 0
    self.CTDIw = 0
    self.CTDIv = 0
    self.current = []

  def initModel(self):
    self.brand_query = QSqlTableModel(db=self.ctx.database.ctdi_db)
    self.scanner_query = QSqlTableModel(db=self.ctx.database.ctdi_db)
    self.volt_query = QSqlTableModel(db=self.ctx.database.ctdi_db)
    self.coll_query = QSqlTableModel(db=self.ctx.database.ctdi_db)

    # fill brand combobox
    self.brand_query.setTable("BRAND")
    self.brand_query.select()
    self.brand_id = self.brand_query.record(0).value("ID")

    # fill scanner combobox
    self.scanner_query.setTable("SCANNER")
    self.scanner_query.setFilter("BRAND_ID=1")
    self.scanner_query.select()
    self.scanner_id = self.scanner_query.record(0).value("ID")

    # fill voltage combobox
    self.volt_query.setTable("CTDI_DATA")
    self.volt_query.setFilter("SCANNER_ID=1")
    self.volt_query.select()
    self.CTDI = self.volt_query.record(0).value("CTDI_HEAD")

    # fill collimation combobox
    self.coll_query.setTable("COLLIMATION_DATA")
    self.coll_query.setFilter("SCANNER_ID=1")
    self.coll_query.select()
    self.coll = self.coll_query.record(0).value("COL_VAL")

  def setModel(self):
    self.brand_cb.setModel(self.brand_query)
    self.brand_cb.setModelColumn(self.brand_query.fieldIndex("NAME"))
    self.scanner_cb.setModel(self.scanner_query)
    self.scanner_cb.setModelColumn(self.scanner_query.fieldIndex("NAME"))
    self.volt_cb.setModel(self.volt_query)
    self.volt_cb.setModelColumn(self.volt_query.fieldIndex("VOLTAGE"))
    self.coll_cb.setModel(self.coll_query)
    self.coll_cb.setModelColumn(self.coll_query.fieldIndex("COL_OPTS"))

  def sigConnect(self):
    self.opts.activated[int].connect(self.on_set_method)
    self.brand_cb.activated[int].connect(self.on_brand_changed)
    self.scanner_cb.activated[int].connect(self.on_scanner_changed)
    self.volt_cb.activated[int].connect(self.on_volt_changed)
    self.coll_cb.activated[int].connect(self.on_coll_changed)
    self.tube_current_edit.textChanged[str].connect(self.on_tube_current_changed)
    self.rotation_time_edit.textChanged[str].connect(self.on_rotation_time_changed)
    self.pitch_edit.textChanged[str].connect(self.on_pitch_changed)
    self.scan_length_c_edit.textChanged[str].connect(self.on_scan_length_changed)
    self.ctdiv_m_edit.textChanged[str].connect(self.on_ctdiv_changed)
    self.dlp_m_edit.textChanged[str].connect(self.on_dlp_changed)
    self.scan_length_d_edit.textChanged[str].connect(self.on_dicom_manual)
    self.ctdiv_d_edit.textChanged[str].connect(self.on_dicom_manual)
    self.tcm_btn.clicked.connect(self.on_get_tcm)

  def initUI(self):
    self.opts = QComboBox()
    self.opts.addItems(['Calculation', 'Input Manually', 'Get from DICOM'])

    self.brand_cb = QComboBox()
    self.scanner_cb = QComboBox()
    self.volt_cb = QComboBox()
    self.coll_cb = QComboBox()

    self.tube_current_edit = QLineEdit(f'{self.tube_current}')
    self.rotation_time_edit = QLineEdit(f'{self.rotation_time}')
    self.pitch_edit = QLineEdit(f'{self.pitch}')
    self.scan_length_c_edit = QLineEdit(f'{self.scan_length}')
    self.scan_length_d_edit = QLineEdit(f'{self.scan_length}')

    self.mas_edit = QLineEdit('0')
    self.mas_eff_edit = QLineEdit('0')
    self.ctdiw_edit = QLineEdit('0')
    self.ctdiv_c_edit = QLineEdit('0')
    self.ctdiv_m_edit = QLineEdit('0')
    self.ctdiv_d_edit = QLineEdit('0')
    self.dlp_c_edit = QLineEdit('0')
    self.dlp_m_edit = QLineEdit('0')
    self.dlp_d_edit = QLineEdit('0')

    self.tcm_btn = QPushButton('TCM')

    self.brand_cb.setPlaceholderText('[Unavailable]')
    self.scanner_cb.setPlaceholderText('[Unavailable]')
    self.volt_cb.setPlaceholderText('[Unavailable]')
    self.coll_cb.setPlaceholderText('[Unavailable]')

    edits = [
      self.tube_current_edit,
      self.rotation_time_edit,
      self.pitch_edit,
      self.scan_length_c_edit,
      self.scan_length_d_edit,
      self.mas_edit,
      self.mas_eff_edit,
      self.ctdiw_edit,
      self.ctdiv_c_edit,
      self.ctdiv_m_edit,
      self.ctdiv_d_edit,
      self.dlp_c_edit,
      self.dlp_m_edit,
      self.dlp_d_edit,
    ]

    [edit.setValidator(QDoubleValidator()) for edit in edits]
    [edit.setMaximumWidth(60) for edit in edits]
    [edit.setAlignment(Qt.AlignRight) for edit in edits]

    self.mas_edit.setReadOnly(True)
    self.mas_eff_edit.setReadOnly(True)
    self.ctdiw_edit.setReadOnly(True)
    self.ctdiv_c_edit.setReadOnly(True)
    self.dlp_c_edit.setReadOnly(True)

    self.set_layout()

  def set_layout(self):
    font = QFont()
    font.setBold(True)
    self.ctdiv_c_edit.setFont(font)
    self.dlp_c_edit.setFont(font)

    manual_grpbox = QGroupBox('')
    manual_layout = QFormLayout()
    manual_layout.addRow(QLabel('CTDI<sub>vol</sub> (mGy)'), self.ctdiv_m_edit)
    manual_layout.addRow(QLabel('DLP (mGy-cm))'), self.dlp_m_edit)
    manual_grpbox.setLayout(manual_layout)
    manual_grpbox.setFont(font)

    dicom_grpbox = QGroupBox('')
    dicom_layout = QFormLayout()
    dicom_layout.addRow(QLabel('Scan Length (cm)'), self.scan_length_d_edit)
    dicom_layout.addRow(QLabel('CTDI<sub>vol</sub> (mGy)'), self.ctdiv_d_edit)
    dicom_layout.addRow(QLabel('DLP (mGy-cm)'), self.dlp_d_edit)
    dicom_grpbox.setLayout(dicom_layout)
    dicom_grpbox.setFont(font)

    calci_grpbox = QGroupBox('')
    calci_layout = QFormLayout()
    calci_layout.addRow(QLabel('Manufacturer'), self.brand_cb)
    calci_layout.addRow(QLabel('Scanner'), self.scanner_cb)
    calci_layout.addRow(QLabel('Voltage (kV)'), self.volt_cb)
    h = QHBoxLayout()
    h.addWidget(self.tube_current_edit)
    h.addWidget(self.tcm_btn)
    h.addStretch()
    calci_layout.addRow(QLabel('Tube Current (mA)'), h)
    calci_layout.addRow(QLabel('Rotation Time (s)'), self.rotation_time_edit)
    calci_layout.addRow(QLabel('Pitch'), self.pitch_edit)
    calci_layout.addRow(QLabel('Collimation (mm)'), self.coll_cb)
    calci_layout.addRow(QLabel('Scan Length (cm)'), self.scan_length_c_edit)
    calci_grpbox.setLayout(calci_layout)

    calco_grpbox = QGroupBox('')
    calco_layout = QFormLayout()
    calco_layout.addRow(QLabel('mAs'), self.mas_edit)
    calco_layout.addRow(QLabel('Effective mAs'), self.mas_eff_edit)
    calco_layout.addRow(QLabel('CTDI<sub>w</sub> (mGy)'), self.ctdiw_edit)
    calco_layout.addRow(QLabel('<b>CTDI<sub>vol</sub> (mGy)</b>'), self.ctdiv_c_edit)
    calco_layout.addRow(QLabel('<b>DLP (mGy-cm)</b>'), self.dlp_c_edit)
    calco_grpbox.setLayout(calco_layout)

    calc_widget = QWidget(self)
    calc_layout = QHBoxLayout()
    calc_layout.addWidget(calco_grpbox)
    calc_layout.addWidget(calci_grpbox)
    calc_layout.setContentsMargins(0,0,0,0)
    calc_widget.setLayout(calc_layout)

    self.stacks = QStackedLayout()
    self.stacks.addWidget(calc_widget)
    self.stacks.addWidget(manual_grpbox)
    self.stacks.addWidget(dicom_grpbox)

    main_layout = QVBoxLayout()
    main_layout.addWidget(QLabel('Options:'))
    main_layout.addWidget(self.opts)
    main_layout.addLayout(self.stacks)

    self.setLayout(main_layout)

  def plot_tcm(self):
    xlabel = 'TCM'
    title = 'Tube Current'
    self.figure = PlotDialog()
    self.figure.plot(self.idxs, self.current, pen={'color': "FFFF00", 'width': 2}, symbol='o', symbolPen=None, symbolSize=8, symbolBrush=(255, 0, 0, 255))
    self.figure.avgLine(self.tube_current)
    self.figure.annotate(pos=(self.idxs[int(len(self.idxs)/2)], self.tube_current), text=f'Avg {xlabel}: {self.tube_current:#.2f} mA')
    self.figure.axes.showGrid(True,True)
    self.figure.setLabels('slice',xlabel,None,'mA')
    self.figure.setTitle(f'Slice - {title}')
    self.figure.show()

  def on_get_tcm(self):
    if not self.ctx.isImage:
      QMessageBox.warning(None, "Warning", "Open DICOM files first, or input manually")
      self.opts.setCurrentIndex(0)
      return
    self.current = []
    self.idxs = []
    try:
      for idx, dcm in enumerate(self.ctx.dicoms):
        self.current.append(float(dcm.XRayTubeCurrent))
        self.idxs.append(idx+1)
    except Exception as e:
      self.current = []
      self.idxs = []
      QMessageBox.warning(None, 'Exception Occured', str(e))
      return
    tube_current = sum(self.current)/self.ctx.total_img
    self.tube_current_edit.setText(f'{tube_current:#.2f}')
    self.tube_current = tube_current
    self.plot_tcm()

  def get_ctdiv_dicom(self):
    try:
      self.CTDIv = float(self.ctx.dicoms[0].CTDIvol)
    except:
      QMessageBox.warning(None, "Warning", "The DICOM does not contain the value of CTDIvol.\nPlease try different method.")
      self.CTDIv = 0

  def get_scan_length_dicom(self):
    try:
      first = float(self.ctx.dicoms[0].SliceLocation)
      last = float(self.ctx.dicoms[-1].SliceLocation)
      width = float(self.ctx.dicoms[0].SliceThickness)
      try:
        second = float(self.ctx.dicoms[1].SliceLocation)
      except:
        second = last
    except Exception as e:
      QMessageBox.warning(None, 'Exception Occured', str(e))
      return

    lf = abs(0.1*(last-first))
    sf = abs(0.1*(second-first))
    print(lf, sf, width/10)
    scan_length = (abs((last-first)) + abs((second-first)) + width)*.1
    self.scan_length = scan_length

  def on_set_method(self, idx):
    self.prev_mode = self.mode
    self.mode = idx
    self.stacks.setCurrentIndex(idx)
    self.calculate()

  def on_brand_changed(self, sel):
    self.brand_id = self.brand_query.record(sel).value("ID")

    self.scanner_query.setFilter(f"BRAND_ID={self.brand_id}")
    self.on_scanner_changed(0)

  def on_scanner_changed(self, sel):
    self.scanner_id = self.scanner_query.record(sel).value("ID")

    self.volt_query.setFilter(f"SCANNER_ID={self.scanner_id}")
    self.coll_query.setFilter(f"SCANNER_ID={self.scanner_id}")
    if self.volt_cb.count() == 0:
      QMessageBox.warning(None, 'No Data', f'There is no CTDI data for this scanner.')
    if self.coll_cb.count() == 0:
      QMessageBox.warning(None, 'No Data', 'There is no collimation data for this scanner.')
    self.on_volt_changed(0)
    self.on_coll_changed(0)

  def on_volt_changed(self, sel):
    phantom = 'head' if self.ctx.phantom==HEAD else 'body'
    self.CTDI = self.volt_query.record(sel).value(f"CTDI_{phantom.upper()}")
    if not self.CTDI and self.volt_cb.count() != 0:
      QMessageBox.warning(None, 'No Data', f'There is no {phantom.capitalize()} CTDI value for this voltage value.')
    self.calculate(False)

  def on_coll_changed(self, sel):
    self.coll = self.coll_query.record(sel).value("COL_VAL")
    if not self.coll and self.coll_cb.count() != 0:
      QMessageBox.warning(None, 'No Data', 'There is no collimation data for this option.')
    self.calculate(False)

  def on_tube_current_changed(self, sel):
    try:
      self.tube_current = float(sel)
    except ValueError:
      self.tube_current = 0
    self.calculate(False)

  def on_rotation_time_changed(self, sel):
    try:
      self.rotation_time = float(sel)
    except ValueError:
      self.rotation_time = 1
    self.calculate(False)

  def on_pitch_changed(self, sel):
    try:
      self.pitch = float(sel)
    except ValueError:
      self.pitch = 1
    self.calculate(False)

  def on_scan_length_changed(self, sel):
    try:
      self.scan_length = float(sel)
    except ValueError:
      self.scan_length = 0
    self.calculate(False)

  def on_dlp_changed(self, sel):
    try:
      self.DLP = float(sel)
    except ValueError:
      self.DLP = 0
    self.set_app_data()

  def on_ctdiv_changed(self, sel):
    try:
      self.CTDIv = float(sel)
    except ValueError:
      self.CTDIv = 0
    self.set_app_data()

  def on_dicom_manual(self):
    try:
      self.CTDIv = float(self.ctdiv_d_edit.text())
    except:
      self.CTDIv = 0
    try:
      self.scan_length = float(self.scan_length_d_edit.text())
    except:
      self.scan_length = 0
    self.DLP = self.CTDIv*self.scan_length
    self.dlp_d_edit.setText(f'{self.DLP:#.2f}')
    self.set_app_data()

  def calculate(self, auto=True):
    if self.mode==0:
      if auto:
        self.scan_length = float(self.scan_length_c_edit.text())
      self.mAs = self.tube_current*self.rotation_time
      try:
        self.eff_mAs = self.tube_current/self.pitch
      except ZeroDivisionError:
        self.eff_mAs = self.tube_current
      try:
        self.CTDIw = self.coll*self.CTDI*self.mAs / 100
      except TypeError:
        self.CTDIw = 0
      try:
        self.CTDIv = self.coll*self.CTDI*self.eff_mAs / 100
      except TypeError:
        self.CTDIv = 0
      self.DLP = self.CTDIv*self.scan_length

      self.mas_edit.setText(f'{self.mAs:#.2f}')
      self.mas_eff_edit.setText(f'{self.eff_mAs:#.2f}')
      self.ctdiw_edit.setText(f'{self.CTDIw:#.2f}')
      self.ctdiv_c_edit.setText(f'{self.CTDIv:#.2f}')
      self.dlp_c_edit.setText(f'{self.DLP:#.2f}')

    elif self.mode==1:
      try:
        self.CTDIv = float(self.ctdiv_m_edit.text())
      except:
        self.CTDIv = 0
      try:
        self.DLP = float(self.dlp_m_edit.text())
      except:
        self.DLP = 0

    elif self.mode==2:
      if not self.ctx.isImage:
        QMessageBox.warning(None, "Warning", "Open DICOM files first.")
        self.opts.setCurrentIndex(self.prev_mode)
        self.on_set_method(self.prev_mode)
        return
      self.get_ctdiv_dicom()
      self.get_scan_length_dicom()

      CTDIv = self.CTDIv
      scan_length = self.scan_length
      DLP = CTDIv*scan_length

      self.ctdiv_d_edit.setText(f'{CTDIv:#.2f}')
      self.scan_length_d_edit.setText(f'{scan_length:#.2f}')

      self.CTDIv = CTDIv
      self.scan_length = scan_length
      self.DLP = DLP

    self.set_app_data()

  def set_app_data(self):
    self.ctx.app_data.CTDIv = self.CTDIv
    self.ctx.app_data.DLP = self.DLP
