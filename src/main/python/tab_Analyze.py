from PyQt5.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QFormLayout, QLabel, QDateEdit, QSpinBox, QComboBox

class AnalyzeTab(QWidget):
  def __init__(self):
    super().__init__()
    self.initUI()

  def initUI(self):
    self.x_cb = QComboBox()
    self.y_cb = QComboBox()
    self.sex_cb = QComboBox()
    self.protocol_cb = QComboBox()
    self.age_sb1 = QSpinBox()
    self.age_sb2 = QSpinBox()
    self.date_edit1 = QDateEdit()
    self.date_edit2 = QDateEdit()
    self.date_edit1.setDisplayFormat('dd/MM/yyyy')
    self.date_edit2.setDisplayFormat('dd/MM/yyyy')

    age_layout = QHBoxLayout()
    age_layout.addWidget(self.age_sb1)
    age_layout.addWidget(self.age_sb2)
    age_layout.addStretch()

    date_layout = QHBoxLayout()
    date_layout.addWidget(self.date_edit1)
    date_layout.addWidget(self.date_edit2)
    date_layout.addStretch()

    self.axis_grpbox = QGroupBox('Axis selection')
    ax_layout = QFormLayout()
    ax_layout.addRow(QLabel('x-axis'), self.x_cb)
    ax_layout.addRow(QLabel('y-axis'), self.y_cb)
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
