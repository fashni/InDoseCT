from PyQt5.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QDateEdit, QSpinBox, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtSql import QSqlTableModel, QSqlQueryModel

class AnalyzeTab(QWidget):
  def __init__(self, ctx):
    super().__init__()
    self.ctx = ctx
    self.query_model = QSqlQueryModel()
    self.initUI()
    self.set_filter()
    self.sig_connect()

  def sig_connect(self):
    self.sex_cb.activated[int].connect(self.on_sex_changed)
    self.protocol_cb.activated[int].connect(self.on_protocol_changed)
    self.age_sb1.valueChanged.connect(self.on_age1_changed)
    self.age_sb2.valueChanged.connect(self.on_age2_changed)
    self.date_edit1.dateChanged.connect(self.on_date1_changed)
    self.date_edit2.dateChanged.connect(self.on_date2_changed)
    self.generate_btn.clicked.connect(self.on_generate)

  def initUI(self):
    self.x_cb = QComboBox()
    self.y_cb = QComboBox()
    self.sex_cb = QComboBox()
    self.protocol_cb = QComboBox()
    self.age_sb1 = QSpinBox()
    self.age_sb2 = QSpinBox()
    self.date_edit1 = QDateEdit()
    self.date_edit2 = QDateEdit()
    self.generate_btn = QPushButton('Generate')

    self.age_sb1.setSpecialValueText('-')
    self.age_sb1.setRange(-1, -1)
    self.age_sb2.setSpecialValueText('-')
    self.age_sb2.setRange(-1, -1)
    self.date_edit1.setDisplayFormat('dd/MM/yyyy')
    self.date_edit2.setDisplayFormat('dd/MM/yyyy')

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
    ax_layout.addWidget(QLabel(''))
    ax_layout.addWidget(self.generate_btn)
    self.axis_grpbox.setLayout(ax_layout)

    self.filter_grpbox = QGroupBox('Filter')
    flt_layout = QFormLayout()
    flt_layout.addRow(QLabel('Sex'), self.sex_cb)
    flt_layout.addRow(QLabel('Protocol'), self.protocol_cb)
    flt_layout.addRow(QLabel('Age'), age_layout)
    flt_layout.addRow(QLabel('Exam Date'), date_layout)
    self.filter_grpbox.setLayout(flt_layout)

    mainlayout = QHBoxLayout()
    mainlayout.addWidget(self.axis_grpbox)
    mainlayout.addWidget(self.filter_grpbox)
    self.setLayout(mainlayout)

  def set_filter(self):
    self.set_protocol()
    self.set_sex()
    self.set_age_range()
    self.set_date_range()

  def set_protocol(self):
    sql = "SELECT DISTINCT Protocol FROM PATIENTS"
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
    sql = "SELECT DISTINCT Sex FROM PATIENTS"
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
    sql = "SELECT MAX(Age) as max FROM PATIENTS"
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
    sql = "SELECT MAX(Date) as max FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    try:
      date_max = QDate.fromString(self.query_model.record(0).value('max'), 'yyyyMMdd')
    except:
      date_max = QDate.currentDate()

    sql = "SELECT MIN(Date) as min FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)
    try:
      date_min = QDate.fromString(self.query_model.record(0).value('min'), 'yyyyMMdd')
    except:
      date_min = QDate(2000,1,1)

    self.date_edit1.setDateRange(date_min, date_max)
    self.date_edit2.setDateRange(date_min, date_max)
    self.date_edit1.setDate(date_min)
    self.date_edit2.setDate(date_max)
    self.date_ftr1 = date_min
    self.date_ftr2 = date_max

  def on_sex_changed(self, idx):
    self.sex_ftr = self.sexes[idx]

  def on_protocol_changed(self, idx):
    self.protocol_ftr = self.protocols[idx]

  def on_age1_changed(self):
    self.age_ftr1 = self.age_sb1.value()

  def on_age2_changed(self):
    self.age_ftr2 = self.age_sb2.value()

  def on_date1_changed(self):
    self.date_ftr1 = self.date_edit1.date()

  def on_date2_changed(self):
    self.date_ftr2 = self.date_edit2.date()

  def on_generate(self):
    QMessageBox.information(None, 'Information', 'This feature is not implemented yet.')
