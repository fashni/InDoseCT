from PyQt5.QtWidgets import (QRadioButton, QGridLayout, QHBoxLayout, QFormLayout, QVBoxLayout, QLineEdit, QLabel, QWidget, QComboBox,
                             QDateEdit, QSpinBox, QAbstractSpinBox)
from PyQt5.QtCore import QDate
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
    self.setInfo(self.getInfo())

  def setUpConnect(self):
    self.name_edit.textChanged.connect(self.on_name_changed)
    self.protocol_edit.textChanged.connect(self.on_protocol_changed)
    self.exam_date_edit.dateChanged.connect(self.on_date_changed)
    self.age_edit.valueChanged.connect(self.on_age_changed)
    self.sex_edit.activated[int].connect(self.on_sex_changed)

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
    self.exam_date_edit = QDateEdit()
    self.age_edit = QSpinBox()
    self.sex_edit = QComboBox()

    self.sex_edit.addItems(['M', 'F', 'Unspecified'])
    self.sex_edit.setPlaceholderText('Unspecified')
    self.sex_edit.setCurrentIndex(2)
    self.exam_date_edit.setDisplayFormat('dd/MM/yyyy')
    self.exam_date_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
    self.age_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)

    l_layout = QFormLayout()
    l_layout.setVerticalSpacing(1)
    l_layout.addRow(no_label, self.no_edit)
    l_layout.addRow(name_label, self.name_edit)
    l_layout.addRow(protocol_label, self.protocol_edit)

    r_layout = QFormLayout()
    r_layout.setVerticalSpacing(1)
    r_layout.addRow(exam_date_label, self.exam_date_edit)
    r_layout.addRow(age_label, self.age_edit)
    r_layout.addRow(sex_label, self.sex_edit)

    main_layout = QHBoxLayout()
    main_layout.addLayout(l_layout)
    main_layout.addLayout(r_layout)

    self.setLayout(main_layout)
    self.setMaximumHeight(75)

  def setInfo(self, pat_info):
    self.name = pat_info['name'] or ''
    self.protocol = pat_info['protocol'] or ''
    self.age = pat_info['age'] or 0
    self.sex = pat_info['sex'] or None
    self.date = pat_info['date'] or None

    self.name_edit.setText(self.name)
    self.protocol_edit.setText(self.protocol)
    self.age_edit.setValue(self.age)
    self.sex_edit.setCurrentText(self.sex) if self.sex is not None else self.sex_edit.setCurrentIndex(2)
    date = QDate.fromString(self.date, 'yyyyMMdd') if self.date is not None else QDate.currentDate()
    self.exam_date_edit.setDate(date)

  def getInfo(self):
    info = {
      'name': self.name or None,
      'sex': self.sex or None,
      'age': self.age or None,
      'protocol': self.protocol or None,
      'date': self.date or None,
      }
    return info

  def on_name_changed(self):
    self.name = self.name_edit.text()

  def on_date_changed(self):
    self.date = self.exam_date_edit.date().toString('yyyyMMdd')

  def on_age_changed(self):
    self.age = self.age_edit.value()

  def on_sex_changed(self, id):
    self.sex = self.sex_edit.currentText() if id != 2 else None
    print(self.sex)

  def on_protocol_changed(self):
    self.protocol = self.protocol_edit.text()
