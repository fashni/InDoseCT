from PyQt5.QtWidgets import QRadioButton, QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QWidget, QComboBox
from db import get_records_num

class InfoPanel(QWidget):
  def __init__(self, ctx, *args, **kwargs):
    super(InfoPanel, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.id = None
    self.name = None
    self.protocol = None
    self.date = None
    self.age = None
    self.sex = None
    self.initUI()
    self.setUpConnect()

  def setUpConnect(self):
    self.name_edit.textChanged.connect(self.on_name_changed)
    self.protocol_edit.textChanged.connect(self.on_protocol_changed)
    self.exam_date_edit.textChanged.connect(self.on_date_changed)
    self.age_edit.textChanged.connect(self.on_age_changed)
    self.sex_edit.textChanged.connect(self.on_sex_changed)

  def initUI(self):
    no_label = QLabel('No')
    name_label = QLabel('Name')
    protocol_label = QLabel('Protocol')
    exam_date_label = QLabel('Exam Date')
    age_label = QLabel('Age')
    sex_label = QLabel('Sex')

    self.no_edit = QLineEdit(str(get_records_num(self.ctx.patients_database(), 'PATIENTS')+1))
    self.name_edit = QLineEdit()
    self.protocol_edit = QLineEdit()
    self.exam_date_edit = QLineEdit()
    self.age_edit = QLineEdit()
    self.sex_edit = QLineEdit()

    grid = QGridLayout()
    grid.setHorizontalSpacing(5)
    grid.setVerticalSpacing(1)

    grid.addWidget(no_label, 0, 0)
    grid.addWidget(self.no_edit, 0, 1)
    grid.addWidget(name_label, 1, 0)
    grid.addWidget(self.name_edit, 1, 1)
    grid.addWidget(protocol_label, 2, 0)
    grid.addWidget(self.protocol_edit, 2, 1)
    grid.addWidget(exam_date_label, 0, 2)
    grid.addWidget(self.exam_date_edit, 0, 3)
    grid.addWidget(age_label, 1, 2)
    grid.addWidget(self.age_edit, 1, 3)
    grid.addWidget(sex_label, 2, 2)
    grid.addWidget(self.sex_edit, 2, 3)

    main_layout = QHBoxLayout()
    main_layout.addLayout(grid)

    self.setLayout(main_layout)
    self.setMaximumHeight(75)

  def setInfo(self, pat_info):
    self.name = pat_info['name'] if pat_info['name'] is not None else ''
    self.age = pat_info['age'][:3] if pat_info['age'] is not None else ''
    self.sex = pat_info['sex'] if pat_info['sex'] is not None else ''
    self.protocol = pat_info['protocol'] if pat_info['protocol'] is not None else ''
    self.date = pat_info['date'] if pat_info['date'] is not None else ''
    self.name_edit.setText(self.name)
    self.age_edit.setText(self.age)
    self.sex_edit.setText(self.sex)
    self.protocol_edit.setText(self.protocol)
    self.exam_date_edit.setText(self.date)

  def getInfo(self):
    info = {'name': self.name if self.name else None,
            'sex': self.sex if self.sex else None,
            'age': self.age if self.age else None,
            'protocol': self.protocol if self.protocol else None,
            'date': self.date if self.date else None,
            }
    return info

  def on_name_changed(self):
    self.name = self.name_edit.text()

  def on_date_changed(self):
    self.date = self.exam_date_edit.text()

  def on_age_changed(self):
    self.age = self.age_edit.text()

  def on_sex_changed(self):
    self.sex = self.sex_edit.text()

  def on_protocol_changed(self):
    self.protocol = self.protocol_edit.text()
