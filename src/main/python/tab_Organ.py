import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import (QComboBox, QFormLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)

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
    self.protocol_cb.activated[int].connect(self.on_protocol_changed)
    self.calc_btn.clicked.connect(self.on_calculate)

  def initUI(self):
    self.figure = PlotDialog()
    self.protocol_cb = QComboBox()
    self.protocol_cb.setModel(self.protocol_model)
    self.protocol_cb.setModelColumn(self.protocol_model.fieldIndex('name'))
    self.calc_btn = QPushButton('Calculate')

    self.organ_labels = []
    self.organ_edits = [QLineEdit('0') for i in range(28)]
    [organ_edit.setMaximumWidth(70) for organ_edit in self.organ_edits]
    [organ_edit.setReadOnly(True) for organ_edit in self.organ_edits]
    [organ_edit.setAlignment(Qt.AlignRight) for organ_edit in self.organ_edits]

    left = QFormLayout()
    right = QFormLayout()
    for idx, organ_edit in enumerate(self.organ_edits):
      name = self.organ_model.record(idx).value('name')
      self.organ_names.append(name[0])
      label = QLabel(name)
      label.setMaximumWidth(100)
      self.organ_labels.append(label)
      left.addRow(label, organ_edit) if idx<14 else right.addRow(label, organ_edit)

    grid = QHBoxLayout()
    grid.addLayout(left)
    grid.addLayout(right)

    organ_grpbox = QGroupBox('Organ Dose')
    organ_grpbox.setLayout(grid)

    scroll = QScrollArea()
    scroll.setWidget(organ_grpbox)
    scroll.setWidgetResizable(True)

    main_layout = QVBoxLayout()
    main_layout.addWidget(QLabel('Protocol:'))
    main_layout.addWidget(self.protocol_cb)
    main_layout.addWidget(self.calc_btn)
    main_layout.addWidget(scroll)
    main_layout.addStretch()

    self.setLayout(main_layout)

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

  def on_protocol_changed(self, idx):
    self.protocol_id = self.protocol_model.record(idx).value("id")
    self.organ_dose_model.setFilter(f'Protocol_ID={self.protocol_id}')
    self.getData()
    print(self.protocol_id, self.protocol_model.record(idx).value("name"))

  def on_calculate(self):
    self.organ_dose = self.ctx.app_data.CTDIv * np.exp(self.alfas*self.ctx.app_data.diameter + self.betas)
    [self.organ_edits[idx].setText(f'{dose:#.2f}') for idx, dose in enumerate(self.organ_dose)]
    self.plot()

  def reset_fields(self):
    [organ_edit.setText('0') for organ_edit in self.organ_edits]
    self.protocol_cb.setCurrentIndex(0)
    self.on_protocol_changed(0)
