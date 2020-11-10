from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QPushButton, QLabel, QWidget, QComboBox, QMessageBox
from PyQt5.QtSql import QSqlTableModel, QSqlQueryModel
from custom_widgets import HSeparator, VSeparator

class CTDIVolTab(QWidget):
  def __init__(self, ctx, *args, **kwargs):
    super(CTDIVolTab, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.initVar()
    self.initModel()
    self.initUI()
    self.sigConnect()
    self.calculate()

  def initVar(self):
    self.mode = 0
    self.CTDI = 0
    self.tube_current = 100
    self.rotation_time = 1
    self.pitch = 1
    self.coll = 0
    self.scan_length = 10
    self.mAs = 0
    self.eff_mAs = 0
    self.CTDIw = 0
    self.current = []

  def initModel(self):
    self.query_model = QSqlQueryModel()
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

  def initUI(self):
    self.setInputFields()
    opt_lbl = QLabel('Options:')

    param_lbls = [
      QLabel('Manufacturer'),
      QLabel('Scanner'),
      QLabel('Voltage (kV)'),
      QLabel('Tube Current (mA)'),
      QLabel('Rotation Time (s)'),
      QLabel('Pitch'),
      QLabel('Collimation (mm)'),
      QLabel('Scan Length (cm)'),
    ]
    tcm_btn = QPushButton('TCM')
    # calc_btn = QPushButton('Calculate')
    tcm_btn.clicked.connect(self.get_tcm)
    # calc_btn.clicked.connect(self.calculate)

    output_lbls = [
      QLabel('mAs'),
      QLabel('Effective mAs'),
      QLabel('CTDIw (mGy)'),
      QLabel('CTDIvol (mGy)'),
      QLabel('DLP (mGy)'),
    ]
    [lbl.setMinimumWidth(150) for lbl in output_lbls]

    layout1 = QVBoxLayout()
    layout1.addWidget(opt_lbl)
    layout1.addWidget(self.opts)

    self.param_layout = QGridLayout()
    [self.param_layout.addWidget(param_lbls[row], row, 0)
      for row in range(len(param_lbls))]
    self.param_layout.addWidget(tcm_btn, 3, 1)
    self.param_layout.addWidget(self.brand_cb, 0, 2)
    self.param_layout.addWidget(self.scanner_cb, 1, 2)
    self.param_layout.addWidget(self.volt_cb, 2, 2)
    self.param_layout.addWidget(self.tube_current_edit, 3, 2)
    self.param_layout.addWidget(self.rotation_time_edit, 4, 2)
    self.param_layout.addWidget(self.pitch_edit, 5, 2)
    self.param_layout.addWidget(self.coll_cb, 6, 2)
    self.param_layout.addWidget(self.scan_length_edit, 7, 2)
    # self.param_layout.addWidget(calc_btn, 8, 0)

    self.output_layout = QGridLayout()
    for row in range(len(output_lbls)):
      self.output_layout.addWidget(output_lbls[row], row, 0)
      self.output_layout.addWidget(self.out_edits[row], row, 1)

    hbox = QHBoxLayout()
    hbox.addLayout(self.output_layout)
    hbox.addStretch()
    hbox.addWidget(VSeparator())
    hbox.addLayout(self.param_layout)
    hbox.addStretch()

    main_layout = QVBoxLayout()
    main_layout.addLayout(layout1)
    main_layout.addWidget(HSeparator())
    main_layout.addLayout(hbox)
    main_layout.addStretch()

    self.setLayout(main_layout)
    self.options(0)

  def sigConnect(self):
    self.opts.activated[int].connect(self.options)
    self.brand_cb.activated[int].connect(self.on_brand_changed)
    self.scanner_cb.activated[int].connect(self.on_scanner_changed)
    self.volt_cb.activated[int].connect(self.on_volt_changed)
    self.coll_cb.activated[int].connect(self.on_coll_changed)
    self.out_edits[3].textChanged[str].connect(self.on_CTDIv_changed)
    self.tube_current_edit.textChanged[str].connect(self.on_tube_current_changed)
    self.rotation_time_edit.textChanged[str].connect(self.on_rotation_time_changed)
    self.pitch_edit.textChanged[str].connect(self.on_pitch_changed)
    self.scan_length_edit.textChanged[str].connect(self.on_scan_length_changed)

  def setInputFields(self):
    self.opts = QComboBox(self)
    self.opts.addItem('Calculation')
    self.opts.addItem('Input Manually')
    self.opts.addItem('Get from DICOM')

    self.brand_cb = QComboBox(self)
    self.brand_cb.setModel(self.brand_query)
    self.brand_cb.setModelColumn(self.brand_query.fieldIndex("NAME"))
    self.scanner_cb = QComboBox(self)
    self.scanner_cb.setModel(self.scanner_query)
    self.scanner_cb.setModelColumn(self.scanner_query.fieldIndex("NAME"))
    self.volt_cb = QComboBox(self)
    self.volt_cb.setModel(self.volt_query)
    self.volt_cb.setModelColumn(self.volt_query.fieldIndex("VOLTAGE"))
    self.coll_cb = QComboBox(self)
    self.coll_cb.setModel(self.coll_query)
    self.coll_cb.setModelColumn(self.coll_query.fieldIndex("COL_OPTS"))

    self.tube_current_edit = QLineEdit(f'{self.tube_current}')
    self.tube_current_edit.setValidator(QDoubleValidator())
    self.tube_current_edit.setMaximumWidth(50)
    self.rotation_time_edit = QLineEdit(f'{self.rotation_time}')
    self.rotation_time_edit.setValidator(QDoubleValidator())
    self.rotation_time_edit.setMaximumWidth(50)
    self.pitch_edit = QLineEdit(f'{self.pitch}')
    self.pitch_edit.setValidator(QDoubleValidator())
    self.pitch_edit.setMaximumWidth(50)
    self.scan_length_edit = QLineEdit(f'{self.scan_length}')
    self.scan_length_edit.setValidator(QDoubleValidator())
    self.scan_length_edit.setMaximumWidth(50)

    self.out_edits = [QLineEdit('0') for i in range(5)]
    [out_edit.setValidator(QDoubleValidator()) for out_edit in self.out_edits]
    [out_edit.setMaximumWidth(50) for out_edit in self.out_edits]

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
    self.CTDI = self.volt_query.record(sel).value(f"CTDI_{self.ctx.phantom.upper()}")
    if not self.CTDI and self.volt_cb.count() != 0:
      QMessageBox.warning(None, 'No Data', f'There is no {self.ctx.phantom.capitalize()} CTDI value for this voltage value.')
    self.calculate()

  def on_coll_changed(self, sel):
    self.coll = self.coll_query.record(sel).value("COL_VAL")
    if not self.coll and self.coll_cb.count() != 0:
      QMessageBox.warning(None, 'No Data', 'There is no collimation data for this option.')
    self.calculate()

  def options(self, sel):
    self.mode = sel
    font = QFont()
    font.setBold(True)
    out_items = [self.output_layout.itemAt(idx) for idx in range(self.output_layout.count())]
    [item.widget().setEnabled(True) for item in out_items]
    param_items = [self.param_layout.itemAt(idx) for idx in range(self.param_layout.count())]
    [item.widget().setEnabled(True) for item in param_items]

    out_items[-1].widget().setFont(font)
    out_items[-2].widget().setFont(font)
    out_items[-3].widget().setFont(font)
    out_items[-4].widget().setFont(font)
    param_items[7].widget().setFont(font)
    param_items[-1].widget().setFont(font)

    if self.mode == 0:
      [item.widget().setEnabled(False) for item in out_items[1::2]]
      font.setBold(False)
      self.scan_length_edit.setFont(font)
      param_items[7].widget().setFont(font)

    elif self.mode == 1:
      [item.widget().setEnabled(False) for item in param_items]
      [item.widget().setEnabled(False) for item in out_items[:6]]
      out_items[-1].widget().setEnabled(False)
      param_items[7].widget().setEnabled(True)
      param_items[-1].widget().setEnabled(True)

    elif self.mode == 2:
      if not self.ctx.isImage:
        QMessageBox.warning(None, "Warning", "Open DICOM files first.")
        self.opts.setCurrentIndex(0)
        self.options(0)
        return
      [item.widget().setEnabled(False) for item in out_items]
      [item.widget().setEnabled(False) for item in param_items]
      out_items[-2].widget().setEnabled(True)
      out_items[-4].widget().setEnabled(True)
      param_items[7].widget().setEnabled(True)
      self.get_from_dicom()

  def on_CTDIv_changed(self, sel):
    if self.mode != 1:
      return
    try:
      self.ctx.app_data.CTDIv = float(sel)
    except ValueError:
      self.ctx.app_data.CTDIv = 0
    self.manual_input()

  def on_scan_length_changed(self, sel):
    if self.mode != 2:
      try:
        self.scan_length = float(sel)
      except ValueError:
        self.scan_length = 0
      if self.mode == 0:
        self.calculate()
      else:
        self.manual_input()

  def on_tube_current_changed(self, sel):
    if self.mode == 0:
      try:
        self.tube_current = float(sel)
      except ValueError:
        self.tube_current = 0
      self.calculate()

  def on_rotation_time_changed(self, sel):
    try:
      self.rotation_time = float(sel)
    except ValueError:
      self.rotation_time = 1
    self.calculate()

  def on_pitch_changed(self, sel):
    try:
      self.pitch = float(sel)
    except ValueError:
      self.pitch = 1
    self.calculate()

  def manual_input(self):
    self.ctx.app_data.DLP = self.scan_length * self.ctx.app_data.CTDIv
    self.out_edits[-1].setText(f'{self.ctx.app_data.DLP:#.2f}')

  def get_from_dicom(self):
    try:
      self.ctx.app_data.CTDIv = float(self.ctx.dicoms[0].CTDIvol)
    except:
      QMessageBox.warning(None, "Warning", "The DICOM doesn't contain value for CTDIvol.\nTry different method.")
      self.ctx.app_data.CTDIv = 0
    self.get_tcm()
    self.ctx.app_data.DLP = self.scan_length * self.ctx.app_data.CTDIv
    self.out_edits[-1].setText(f'{self.ctx.app_data.DLP:#.2f}')
    self.out_edits[-2].setText(f'{self.ctx.app_data.CTDIv:#.2f}')

  def calculate(self):
    self.mAs = self.tube_current*self.rotation_time
    self.eff_mAs = self.tube_current/self.pitch
    try:
      self.CTDIw = self.coll*self.CTDI*self.mAs / 100
    except TypeError:
      self.CTDIw = 0
    try:
      self.ctx.app_data.CTDIv = self.coll*self.CTDI*self.eff_mAs / 100
    except TypeError:
      self.ctx.app_data.CTDIv = 0
    self.ctx.app_data.DLP = self.ctx.app_data.CTDIv*self.scan_length

    self.out_edits[0].setText(f'{self.mAs:#.2f}')
    self.out_edits[1].setText(f'{self.eff_mAs:#.2f}')
    self.out_edits[2].setText(f'{self.CTDIw:#.2f}')
    self.out_edits[3].setText(f'{self.ctx.app_data.CTDIv:#.2f}')
    self.out_edits[4].setText(f'{self.ctx.app_data.DLP:#.2f}')

  def printinfo(self):
    print('Brand_id: ', self.brand_id)
    print('Scanner_id: ', self.scanner_id)
    print('Volt: ', self.volt_query.record(self.volt_cb.currentIndex()).value("VOLTAGE"))
    print('Phantom: ', self.ctx.phantom)
    print('CTDI: ', self.CTDI)
    print('Coll_opt: ', self.coll_query.record(self.coll_cb.currentIndex()).value("COL_OPTS"))
    print('Coll_val: ', self.coll)
    print('')

  def get_tcm(self):
    if not self.ctx.isImage:
      QMessageBox.warning(None, "Warning", "Open DICOM files first, or input manually")
      self.opts.setCurrentIndex(0)
      return
    self.current = []
    for dcm in self.ctx.dicoms:
      self.current.append(float(dcm.XRayTubeCurrent))
    tube_current = sum(self.current)/self.ctx.total_img
    self.tube_current_edit.setText(f'{tube_current:#.2f}')
    self.tube_current = tube_current

    first = float(self.ctx.dicoms[0].SliceLocation)
    last = float(self.ctx.dicoms[-1].SliceLocation)
    scan_length = abs(0.1*(last-first))
    self.scan_length_edit.setText(f'{scan_length:#.2f}')
    self.scan_length = scan_length
