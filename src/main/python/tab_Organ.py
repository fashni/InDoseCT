from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QScrollArea, QRadioButton, QButtonGroup, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlTableModel
import pyqtgraph as pg
import numpy as np
from custom_widgets import HSeparator, VSeparator, Label
from constants import *
from Plot import PlotDialog, AxisItem

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
    self.protocol.activated[int].connect(self.on_protocol_changed)
    self.calc_btn.clicked.connect(self.on_calculate)

  def initUI(self):
    prot_lbl = QLabel('Protocol:')
    self.protocol = QComboBox()
    self.protocol.setModel(self.protocol_model)
    self.protocol.setModelColumn(self.protocol_model.fieldIndex('name'))
    self.calc_btn = QPushButton('Calculate')

    self.organ_edits = [QLineEdit('0') for i in range(28)]
    [organ_edit.setMaximumWidth(70) for organ_edit in self.organ_edits]
    [organ_edit.setReadOnly(True) for organ_edit in self.organ_edits]
    [organ_edit.setAlignment(Qt.AlignRight) for organ_edit in self.organ_edits]

    self.organ_labels = []

    grid = QGridLayout()
    grid.setHorizontalSpacing(0)
    grid.setVerticalSpacing(1)

    for col in range(2):
      for row in range(14):
        grid.addWidget(self.organ_edits[14*col+row], row, 2*col+1)

    for col in range(2):
      for row in range(14):
        name = self.organ_model.record(14*col+row).value('name')
        self.organ_names.append(name[0])
        label = Label(100, name)
        label.adjustSize()
        self.organ_labels.append(label)
        grid.addWidget(self.organ_labels[14*col+row], row, 2*col)

    main_layout = QVBoxLayout()
    main_layout.addWidget(prot_lbl)
    main_layout.addWidget(self.protocol)
    main_layout.addWidget(self.calc_btn)
    main_layout.addWidget(HSeparator())
    main_layout.addLayout(grid)
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
    [self.organ_edits[idx].setText(f'{dose:#.4f}') for idx, dose in enumerate(self.organ_dose)]
    self.plot()
