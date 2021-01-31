import numpy as np
from PyQt5.QtCore import QDate
from PyQt5.QtSql import QSqlQueryModel, QSqlTableModel
from PyQt5.QtWidgets import (QComboBox, QDateEdit, QFormLayout, QGroupBox,
                             QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QSpinBox, QWidget)

from Plot import PlotDialog


class AnalyzeTab(QWidget):
  def __init__(self, ctx):
    super().__init__()
    self.ctx = ctx
    self.bins = 20
    self.initVar()
    self.initModel()
    self.initUI()
    self.set_axis_opts()
    self.set_filter()
    self.sigConnect()
    self.apply_filter()

  def initVar(self):
    self.x_opts = ['Record ID', 'CTDIvol', 'Age', 'Deff', 'Dw', 'SSDE', 'Effective Dose', 'DLP', 'DLPc']
    self.x_units = ['', 'mGy', 'Year', 'cm', 'cm', 'mGy', 'mSv', 'mGy-cm', 'mGy-cm']
    self.y_opts = ['CTDIvol', 'Age', 'Deff', 'Dw', 'SSDE', 'Effective Dose', 'DLP', 'DLPc', 'Frequency']
    self.y_units = ['mGy', 'Year', 'cm', 'cm', 'mGy', 'mSv', 'mGy-cm', 'mGy-cm', '']

    self.age_ftr1 = -1
    self.age_ftr2 = -1
    self.date_ftr1 = QDate.currentDate()
    self.date_ftr2 = QDate.currentDate()
    self.brand_ftr = 'All'
    self.instn_ftr = 'All'
    self.protocol_ftr = 'All'
    self.scanner_ftr = 'All'
    self.sex_ftr = 'All'

    self.x_opt = self.x_opts[0]
    self.y_opt = self.y_opts[0]

  def initModel(self):
    self.query_model = QSqlQueryModel()
    self.data_query_model = QSqlQueryModel()

  def sigConnect(self):
    self.x_cb.activated[str].connect(self.on_x_changed)
    self.y_cb.activated[str].connect(self.on_y_changed)
    self.sex_cb.activated[int].connect(self.on_sex_changed)
    self.protocol_cb.activated[int].connect(self.on_protocol_changed)
    self.instn_cb.activated[int].connect(self.on_instn_changed)
    self.brand_cb.activated[int].connect(self.on_brand_changed)
    self.scanner_cb.activated[int].connect(self.on_scanner_changed)
    self.age_sb1.valueChanged.connect(self.on_age1_changed)
    self.age_sb2.valueChanged.connect(self.on_age2_changed)
    self.date_edit1.dateChanged.connect(self.on_date1_changed)
    self.date_edit2.dateChanged.connect(self.on_date2_changed)
    self.bins_sb.valueChanged.connect(self.on_bins_changed)
    self.generate_btn.clicked.connect(self.on_generate)
    self.reset_btn.clicked.connect(self.set_filter)

  def initUI(self):
    self.figure = PlotDialog()
    self.x_cb = QComboBox()
    self.y_cb = QComboBox()
    self.sex_cb = QComboBox()
    self.protocol_cb = QComboBox()
    self.age_sb1 = QSpinBox()
    self.age_sb2 = QSpinBox()
    self.date_edit1 = QDateEdit()
    self.date_edit2 = QDateEdit()
    self.generate_btn = QPushButton('Generate')
    self.bins_sb = QSpinBox()
    self.bins_lbl = QLabel('Bins')
    self.reset_btn = QPushButton('Reset Filter')
    self.brand_cb = QComboBox()
    self.scanner_cb = QComboBox()
    self.instn_cb = QComboBox()
    self.data_count_lbl = QLabel(str(self.data_query_model.rowCount()))

    self.age_sb1.setSpecialValueText('-')
    self.age_sb1.setRange(-1, -1)
    self.age_sb1.setMinimumWidth(90)
    self.age_sb2.setSpecialValueText('-')
    self.age_sb2.setRange(-1, -1)
    self.age_sb2.setMinimumWidth(90)
    self.date_edit1.setDisplayFormat('dd/MM/yyyy')
    self.date_edit1.setMinimumWidth(90)
    self.date_edit2.setDisplayFormat('dd/MM/yyyy')
    self.date_edit2.setMinimumWidth(90)
    self.bins_sb.setMinimum(1)
    self.bins_sb.setValue(self.bins)
    self.bins_sb.setVisible(False)
    self.bins_lbl.setVisible(False)

    age_layout = QHBoxLayout()
    age_layout.addWidget(self.age_sb1)
    age_layout.addWidget(QLabel('to'))
    age_layout.addWidget(self.age_sb2)
    age_layout.addStretch()

    date_layout = QHBoxLayout()
    date_layout.addWidget(self.date_edit1)
    date_layout.addWidget(QLabel('to'))
    date_layout.addWidget(self.date_edit2)
    date_layout.addStretch()

    self.axis_grpbox = QGroupBox('Axis selection')
    ax_layout = QFormLayout()
    ax_layout.addRow(QLabel('x-axis'), self.x_cb)
    ax_layout.addRow(QLabel('y-axis'), self.y_cb)
    ax_layout.addRow(self.bins_lbl, self.bins_sb)
    ax_layout.addWidget(self.generate_btn)
    self.axis_grpbox.setLayout(ax_layout)

    self.filter_grpbox = QGroupBox('Filter')
    flt_layout = QFormLayout()
    flt_layout.addRow(QLabel('Institution'), self.instn_cb)
    flt_layout.addRow(QLabel('Manufacturer'), self.brand_cb)
    flt_layout.addRow(QLabel('Scanner'), self.scanner_cb)
    flt_layout.addRow(QLabel('Protocol'), self.protocol_cb)
    flt_layout.addRow(QLabel('Sex'), self.sex_cb)
    flt_layout.addRow(QLabel('Age'), age_layout)
    flt_layout.addRow(QLabel('Exam Date'), date_layout)
    flt_layout.addRow(QLabel('Data Count'), self.data_count_lbl)
    flt_layout.addWidget(self.reset_btn)
    self.filter_grpbox.setLayout(flt_layout)

    mainlayout = QHBoxLayout()
    mainlayout.addWidget(self.axis_grpbox)
    mainlayout.addWidget(self.filter_grpbox)
    self.setLayout(mainlayout)

  def set_filter(self):
    self.set_instn()
    self.set_brand()
    self.set_scanner()
    self.set_protocol()
    self.set_sex()
    self.set_age_range()
    self.set_date_range()

  def set_instn(self):
    sql = "SELECT DISTINCT institution FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    self.instns = [self.query_model.record(idx).value('Institution') for idx in range(self.query_model.rowCount())]
    try:
      self.instns[self.instns.index('')] = 'Unspecified'
    except:
      pass
    self.instns.insert(0, 'All')
    self.instn_cb.clear()
    self.instn_cb.addItems(self.instns)
    self.on_instn_changed(0)

  def set_brand(self):
    sql = "SELECT DISTINCT manufacturer FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    self.brands = [self.query_model.record(idx).value('Manufacturer') for idx in range(self.query_model.rowCount())]
    try:
      self.brands[self.brands.index('')] = 'Unspecified'
    except:
      pass
    self.brands.insert(0, 'All')
    self.brand_cb.clear()
    self.brand_cb.addItems(self.brands)
    self.on_brand_changed(0)

  def set_scanner(self, filter=None):
    if filter is not None:
      sql = f'SELECT DISTINCT model FROM PATIENTS WHERE manufacturer="{filter}"'
      self.query_model.setQuery(sql, self.ctx.database.patient_db)
      self.scanners = [self.query_model.record(idx).value('Model') for idx in range(self.query_model.rowCount())]
      try:
        self.scanners[self.scanners.index('')] = 'Unspecified'
      except:
        print('gagal')
    else:
      self.scanners = ['Unspecified']
    self.scanners.insert(0, 'All')
    self.scanner_cb.clear()
    self.scanner_cb.addItems(self.scanners)
    self.on_scanner_changed(0)

  def set_protocol(self):
    sql = "SELECT DISTINCT protocol FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    self.protocols = [self.query_model.record(idx).value('Protocol') for idx in range(self.query_model.rowCount())]
    try:
      self.protocols[self.protocols.index('')] = 'Unspecified'
    except:
      pass
    self.protocols.insert(0, 'All')
    self.protocol_cb.clear()
    self.protocol_cb.addItems(self.protocols)
    self.on_protocol_changed(0)

  def set_sex(self):
    sql = "SELECT DISTINCT sex FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    self.sexes = [self.query_model.record(idx).value('Sex') for idx in range(self.query_model.rowCount())]
    try:
      self.sexes[self.sexes.index('')] = 'Unspecified'
    except:
      pass
    self.sexes.insert(0, 'All')
    self.sex_cb.clear()
    self.sex_cb.addItems(self.sexes)
    self.on_sex_changed(0)

  def set_age_range(self):
    sql = "SELECT MAX(age) as max FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    try:
      age_max = int(self.query_model.record(0).value('max'))
    except:
      age_max = -1

    self.age_sb1.setRange(-1, age_max)
    self.age_sb1.setValue(-1)
    self.age_sb2.setRange(-1, age_max)
    self.age_sb2.setValue(-1)
    self.age_ftr1 = -1
    self.age_ftr2 = -1

  def set_date_range(self):
    sql = "SELECT MAX(exam_date) as max FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    try:
      date_max = QDate.fromString(self.query_model.record(0).value('max'), 'yyyyMMdd')
    except:
      date_max = QDate.currentDate()

    sql = "SELECT MIN(exam_date) as min FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    try:
      date_min = QDate.fromString(self.query_model.record(0).value('min'), 'yyyyMMdd')
    except:
      date_min = QDate(2000,1,1)

    self.date_edit1.setDate(date_min)
    self.date_edit2.setDate(date_max)
    self.date_ftr1 = date_min
    self.date_ftr2 = date_max

  def set_axis_opts(self):
    sql = "SELECT * FROM PATIENTS LIMIT 1"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    self.x_cb.clear()
    self.y_cb.clear()
    self.x_cb.addItems(self.x_opts)
    self.y_cb.addItems(self.y_opts)
    self.on_x_changed(self.x_opts[0])
    self.on_y_changed(self.y_opts[0])

  def on_x_changed(self, sel):
    if sel=='Dw' or sel=='Deff':
      dw = self.y_cb.findText('Dw')
      de = self.y_cb.findText('Deff')
      self.y_cb.removeItem(dw)
      self.y_cb.removeItem(de)
    else:
      y_txt = self.y_cb.currentText()
      self.y_cb.clear()
      self.y_cb.addItems(self.y_opts)
      self.y_cb.setCurrentText(y_txt)
    unit_idx = self.x_opts.index(sel)
    self.x_unit = self.x_units[unit_idx]
    self.x_opt = sel
    self.apply_filter()

  def on_y_changed(self, sel):
    if sel=='Frequency':
      self.bins_lbl.setVisible(True)
      self.bins_sb.setVisible(True)
    else:
      self.bins_lbl.setVisible(False)
      self.bins_sb.setVisible(False)
    if sel=='Dw' or sel=='Deff':
      dw = self.x_cb.findText('Dw')
      de = self.x_cb.findText('Deff')
      self.x_cb.removeItem(dw)
      self.x_cb.removeItem(de)
    else:
      x_txt = self.x_cb.currentText()
      self.x_cb.clear()
      self.x_cb.addItems(self.x_opts)
      self.x_cb.setCurrentText(x_txt)
    unit_idx = self.y_opts.index(sel)
    self.y_unit = self.y_units[unit_idx]
    self.y_opt = sel
    self.apply_filter()

  def on_instn_changed(self, idx):
    self.instn_ftr = self.instns[idx]
    self.apply_filter()

  def on_brand_changed(self, idx):
    self.brand_ftr = self.brands[idx]
    self.set_scanner(self.brand_ftr if idx!=0 else None)
    self.apply_filter()

  def on_scanner_changed(self, idx):
    self.scanner_ftr = self.scanners[idx]
    self.apply_filter()

  def on_sex_changed(self, idx):
    self.sex_ftr = self.sexes[idx]
    self.apply_filter()

  def on_protocol_changed(self, idx):
    self.protocol_ftr = self.protocols[idx]
    self.apply_filter()

  def on_age1_changed(self):
    self.age_ftr1 = self.age_sb1.value()
    self.apply_filter()

  def on_age2_changed(self):
    self.age_ftr2 = self.age_sb2.value()
    self.apply_filter()

  def on_date1_changed(self):
    self.date_ftr1 = self.date_edit1.date()
    self.apply_filter()

  def on_date2_changed(self):
    self.date_ftr2 = self.date_edit2.date()
    self.apply_filter()

  def on_bins_changed(self):
    self.bins = self.bins_sb.value()
    self.apply_filter()

  def get_data(self):
    sql = f"SELECT {self.x_name}, {self.y_name} FROM PATIENTS WHERE {self.filter} ORDER BY {self.x_name}"
    self.data_query_model.setQuery(sql, self.ctx.database.patient_db)
    self.x_data = np.array([self.data_query_model.record(n).value(self.x_name) for n in range(self.data_query_model.rowCount())])

    if self.y_opt!='Frequency':
      self.y_data = np.array([self.data_query_model.record(n).value(self.y_name) for n in range(self.data_query_model.rowCount())])
    else:
      hist, bin_edges = np.histogram(self.x_data, bins=self.bins)
      bin_width = bin_edges[1]-bin_edges[0]
      self.x_data = bin_edges#[:-1] + bin_width/2
      self.y_data = hist

  def apply_sex_filter(self):
    if self.sex_ftr!='All':
      if self.filter:
        self.filter += ' AND '
      if self.sex_ftr=='Unspecified':
        self.filter += 'sex is NULL'
      else:
        self.filter += f'sex="{self.sex_ftr}"'

  def apply_protocol_filter(self):
    if self.protocol_ftr!='All':
      if self.filter:
        self.filter += ' AND '
      if self.protocol_ftr=='Unspecified':
        self.filter += 'protocol is NULL'
      else:
        self.filter += f'protocol="{self.protocol_ftr}"'

  def apply_instn_filter(self):
    if self.instn_ftr!='All':
      if self.filter:
        self.filter += ' AND '
      if self.instn_ftr=='Unspecified':
        self.filter += 'institution is NULL'
      else:
        self.filter += f'institution="{self.instn_ftr}"'

  def apply_brand_filter(self):
    if self.brand_ftr!='All':
      if self.filter:
        self.filter += ' AND '
      if self.brand_ftr=='Unspecified':
        self.filter += 'manufacturer is NULL'
      else:
        self.filter += f'manufacturer="{self.brand_ftr}"'

  def apply_scanner_filter(self):
    if self.scanner_ftr!='All':
      if self.filter:
        self.filter += ' AND '
      if self.scanner_ftr=='Unspecified':
        self.filter += 'model is NULL'
      else:
        self.filter += f'model="{self.scanner_ftr}"'

  def apply_age_filter(self):
    if self.age_ftr1 != -1 and self.age_ftr2 != -1:
      if self.age_ftr1 <= self.age_ftr2:
        lo_age = self.age_ftr1
        hi_age = self.age_ftr2
      else:
        lo_age = self.age_ftr2
        hi_age = self.age_ftr1
      if self.filter:
        self.filter += ' AND '
      self.filter += f'age BETWEEN {lo_age} and {hi_age}'

  def apply_date_filter(self):
    if self.filter:
      self.filter += ' AND '
    if self.date_ftr1.toString('yyyyMMdd') <= self.date_ftr2.toString('yyyyMMdd'):
      lo_date = self.date_ftr1.toString('yyyyMMdd')
      hi_date = self.date_ftr2.toString('yyyyMMdd')
    else:
      lo_date = self.date_ftr2.toString('yyyyMMdd')
      hi_date = self.date_ftr1.toString('yyyyMMdd')
    self.filter += f'exam_date BETWEEN {lo_date} and {hi_date}'

  def set_x_data(self):
    if self.x_opt == 'Record ID':
      self.x_name = 'id'
    elif self.x_opt == 'Effective Dose':
      self.x_name = 'effective_dose'
    elif self.x_opt == 'Deff' or self.x_opt == 'Dw':
      self.x_name = 'diameter'
      if self.filter:
        self.filter += ' AND '
      self.filter += f'diameter_type="{self.x_opt}"'
    else:
      self.x_name = self.x_opt

  def set_y_data(self):
    if self.y_opt == 'Effective Dose':
      self.y_name = 'effective_dose'
    elif self.y_opt == 'Deff' or self.y_opt == 'Dw':
      self.y_name = 'diameter'
      if self.filter:
        self.filter += ' AND '
      self.filter += f'diameter_type="{self.y_opt}"'
    elif self.y_opt == 'Frequency':
      self.y_name = 'NULL'
    else:
      self.y_name = self.y_opt

    if self.filter:
      self.filter += ' AND '
    if self.y_opt!='Frequency':
      self.filter += f'{self.x_name} is NOT NULL AND {self.y_name} is NOT NULL'
    else:
      self.filter += f'{self.x_name} is NOT NULL'

  def apply_filter(self):
    self.filter = ''
    self.apply_sex_filter()
    self.apply_protocol_filter()
    self.apply_instn_filter()
    self.apply_brand_filter()
    self.apply_scanner_filter()
    self.apply_age_filter()
    self.apply_date_filter()

    self.set_x_data()
    self.set_y_data()
    self.get_data()
    self.data_count_lbl.setText(str(self.data_query_model.rowCount()))

  def plot(self):
    self.figure = PlotDialog()
    self.figure.axes.addLegend(pen='w', brush=(64,64,64,127))
    if self.y_opt=='Frequency':
      self.figure.plot(self.x_data, self.y_data, name=f'{self.x_opt} {self.y_opt}', stepMode=True, fillLevel=0, brush=(0,0,255,150), symbol='o', symbolSize=5)
    else:
      self.figure.actionEnabled(True)
      self.figure.plot(self.x_data, self.y_data, name='data points', pen=None, symbol='o', symbolSize=8, symbolPen='k', symbolBrush=(255, 255, 0, 255))
    self.figure.axes.showGrid(True,True)
    self.figure.setLabels(self.x_opt, self.y_opt, self.x_unit, self.y_unit)
    self.figure.setTitle(f'{self.x_opt} - {self.y_opt}')
    self.figure.show()

  def on_generate(self):
    print(self.filter)
    isempty = lambda arr: arr.size==0
    if isempty(self.x_data) or isempty(self.y_data):
      QMessageBox.information(None, "No Data", "Matching data not found.\nPlease try to reduce the filter.")
      return
    self.plot()

  def reset_fields(self):
    self.set_filter()
    self.bins_sb.setValue(20)
    self.x_cb.setCurrentIndex(0)
    self.y_cb.setCurrentIndex(0)
    self.on_bins_changed()
    self.on_x_changed(self.x_cb.currentText)
    self.on_y_changed(self.x_cb.currentText)
