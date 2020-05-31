from PyQt5.QtWidgets import QGridLayout, QLineEdit, QLabel, QWidget, QComboBox

class InfoPanel(QWidget):
  def __init__(self, *args, **kwargs):
    super(InfoPanel, self).__init__(*args, **kwargs)
    self.initUI()

  def initUI(self):
    no_label = QLabel('No')
    name_label = QLabel('Name')
    protocol_label = QLabel('Protocol')
    exam_date_label = QLabel('Exam Date')
    age_label = QLabel('Age')
    sex_label = QLabel('Sex')
    
    self.no_edit = QLineEdit()
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

    self.setLayout(grid)
    self.setMaximumHeight(75)

  def setInfo(self, pat_info):
    self.name_edit.setText(pat_info['name'])
    self.age_edit.setText(pat_info['age'][:3])
    self.sex_edit.setText(pat_info['sex'])
    self.protocol_edit.setText(pat_info['protocol'])
    self.exam_date_edit.setText(pat_info['date'])
