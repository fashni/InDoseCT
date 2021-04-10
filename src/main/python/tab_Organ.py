import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QScrollArea, QStackedWidget, QVBoxLayout, QWidget)

from constants import *
from Plot import AxisItem, PlotDialog


class OrganTab(QWidget):
  def __init__(self, ctx, *args, **kwargs):
    super(OrganTab, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.initModel()
    self.initVar()
    self.initUI()
    self.sigConnect()

  def initVar(self):
    self.is_accel = False
    self.alfas = None
    self.betas = None
    self.organ_dose = None
    self.organ_names = []

  def initModel(self):
    self.protocol_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.organ_model = QSqlTableModel(db=self.ctx.database.ssde_db)
    self.organ_dose_model = QSqlTableModel(db=self.ctx.database.ssde_db)

    self.protocol_model.setTable("Protocol")
    self.organ_model.setTable("Organ")
    self.organ_dose_model.setTable("Organ_Dose")

    self.protocol_model.setFilter("Group_ID=1")
    self.organ_dose_model.setFilter("Protocol_ID=1")

    self.protocol_model.select()
    self.organ_model.select()
    self.organ_dose_model.select()

  def sigConnect(self):
    self.method_cb.activated[int].connect(self.on_method_changed)
    self.protocol_cb.activated[int].connect(self.on_protocol_changed)
    self.calc_db_btn.clicked.connect(self.on_calculate_db)
    self.calc_cnt_btn.clicked.connect(self.on_calculate_cnt)
    self.add_cnt_btn.clicked.connect(self.on_contour)
    self.is_accelerated_chk.stateChanged.connect(self.on_accelerated_check)

  def initUI(self):
    self.figure = PlotDialog()
    self.method_cb = QComboBox()
    self.method_cb.addItems(['Database', 'Contour'])

    self.init_db_method_ui()
    self.init_cnt_method_ui()

    self.main_area = QStackedWidget()
    self.main_area.addWidget(self.db_method_ui)
    self.main_area.addWidget(self.cnt_method_ui)
    self.on_method_changed()

    main_layout = QVBoxLayout()
    main_layout.addWidget(QLabel('Method:'))
    main_layout.addWidget(self.method_cb)
    main_layout.addWidget(self.main_area)
    main_layout.addStretch()

    self.setLayout(main_layout)

  def init_db_method_ui(self):
    self.protocol_cb = QComboBox()
    self.protocol_cb.setModel(self.protocol_model)
    self.protocol_cb.setModelColumn(self.protocol_model.fieldIndex('name'))
    self.calc_db_btn = QPushButton('Calculate')

    self.organ_labels = []
    self.organ_edits = [QLineEdit('0') for i in range(28)]
    [organ_edit.setMaximumWidth(70) for organ_edit in self.organ_edits]
    [organ_edit.setReadOnly(True) for organ_edit in self.organ_edits]
    [organ_edit.setAlignment(Qt.AlignRight) for organ_edit in self.organ_edits]

    left = QFormLayout()
    right = QFormLayout()
    grid = QHBoxLayout()
    organ_grpbox = QGroupBox('Organ Dose')
    scroll = QScrollArea()

    for idx, organ_edit in enumerate(self.organ_edits):
      name = self.organ_model.record(idx).value('name')
      self.organ_names.append(name[0])
      label = QLabel(name)
      label.setMaximumWidth(100)
      self.organ_labels.append(label)
      left.addRow(label, organ_edit) if idx<14 else right.addRow(label, organ_edit)

    grid.addLayout(left)
    grid.addLayout(right)
    organ_grpbox.setLayout(grid)
    scroll.setWidget(organ_grpbox)
    scroll.setWidgetResizable(True)

    self.db_method_ui = QGroupBox('', self)
    db_method_layout = QVBoxLayout()
    db_method_layout.addWidget(QLabel('Protocol:'))
    db_method_layout.addWidget(self.protocol_cb)
    db_method_layout.addWidget(self.calc_db_btn)
    db_method_layout.addWidget(scroll)
    db_method_layout.addStretch()
    self.db_method_ui.setLayout(db_method_layout)

  def init_cnt_method_ui(self):
    self.calc_cnt_btn = QPushButton('Calculate')
    self.add_cnt_btn = QPushButton('Add Contour')
    self.is_accelerated_chk = QCheckBox('Accelerated Mode')

    self.ctdivol_edit = QLineEdit()
    self.ssdew_edit = QLineEdit()
    self.ssdec_edit = QLineEdit()
    self.ssdep_edit = QLineEdit()
    self.mean_edit = QLineEdit()
    self.std_edit = QLineEdit()

    left = QGroupBox('', self)
    right = QGroupBox('', self)
    left_layout = QFormLayout()
    right_layout = QFormLayout()

    left_layout.addRow(QLabel("<b>CTDI<sub>vol</sub> (mGy)</b>"), self.ctdivol_edit)
    left_layout.addRow(QLabel("<b>SSDE<sub>w</sub> (mGy)</b>"), self.ssdew_edit)
    left_layout.addRow(QLabel("<b>SSDE<sub>c</sub> (mGy)</b>"), self.ssdec_edit)
    left_layout.addRow(QLabel("<b>SSDE<sub>p</sub> (mGy)</b>"), self.ssdep_edit)
    right_layout.addRow(QLabel("<b>Mean (mGy)</b>"), self.mean_edit)
    right_layout.addRow(QLabel("<b>Std. Deviation (mGy)</b>"), self.std_edit)
    left.setLayout(left_layout)
    right.setLayout(right_layout)

    output_area = QHBoxLayout()
    output_area.addWidget(left)
    output_area.addWidget(right)

    main_layout = QVBoxLayout()
    main_layout.addLayout(output_area)
    main_layout.addWidget(self.add_cnt_btn)
    main_layout.addWidget(self.calc_cnt_btn)
    main_layout.addWidget(self.is_accelerated_chk)

    self.cnt_method_ui = QGroupBox('', self)
    self.cnt_method_ui.setLayout(main_layout)

  def plot(self):
    xdict = dict(enumerate(self.organ_names, 1))
    stringaxis = AxisItem(orientation='bottom')
    stringaxis.setTicks([xdict.items()])
    # fm = QFontMetrics(stringaxis.font())
    # minHeight = max(fm.boundingRect(QRect(), Qt.AlignLeft, t).width() for t in xdict.values())
    # stringaxis.setHeight(minHeight + fm.width('     '))

    self.figure = PlotDialog(size=(900,600), straxis=stringaxis)
    self.figure.setTitle('Organ Dose')
    self.figure.axes.showGrid(False,True)
    self.figure.setLabels('', 'Dose' ,'', 'mGy')
    self.figure.bar(x=list(xdict.keys()), height=self.organ_dose, width=.8, brush='g')
    self.figure.show()

  def getData(self):
    self.alfas = np.array([self.organ_dose_model.record(n).value('alfa') for n in range(self.organ_dose_model.rowCount())])
    self.betas = np.array([self.organ_dose_model.record(n).value('beta') for n in range(self.organ_dose_model.rowCount())])

  def on_method_changed(self):
    self.main_area.setCurrentIndex(self.method_cb.currentIndex())

  def on_protocol_changed(self, idx):
    self.protocol_id = self.protocol_model.record(idx).value("id")
    self.organ_dose_model.setFilter(f'Protocol_ID={self.protocol_id}')
    self.getData()
    print(self.protocol_id, self.protocol_model.record(idx).value("name"))

  def on_calculate_db(self):
    self.organ_dose = self.ctx.app_data.CTDIv * np.exp(self.alfas*self.ctx.app_data.diameter + self.betas)
    [self.organ_edits[idx].setText(f'{dose:#.2f}') for idx, dose in enumerate(self.organ_dose)]
    self.plot()

  def on_calculate_cnt(self):
    print(self.is_accel)

  def on_contour(self):
    pass

  def on_accelerated_check(self, state):
    self.is_accel = state == Qt.Checked

  def reset_fields(self):
    [organ_edit.setText('0') for organ_edit in self.organ_edits]
    self.protocol_cb.setCurrentIndex(0)
    self.on_protocol_changed(0)
