from PyQt5.QtWidgets import QRadioButton, QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QWidget, QComboBox
from custom_widgets import VSeparator, GetMainWindowProps
from db import get_records_num

class InfoPanel(QWidget):
  def __init__(self, ctx, *args, **kwargs):
    super(InfoPanel, self).__init__(*args, **kwargs)
    self.ctx = ctx
    self.first_run = True
    self.initUI()

  def initUI(self):
    no_label = QLabel('No')
    name_label = QLabel('Name')
    protocol_label = QLabel('Protocol')
    exam_date_label = QLabel('Exam Date')
    age_label = QLabel('Age')
    sex_label = QLabel('Sex')
    
    self.no_edit = QLineEdit(str(get_records_num(self.ctx.patients_database())+1))
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

    phantom_lbl = QLabel('Phantom:')
    body_btn = QRadioButton('Body')
    head_btn = QRadioButton('Head')
    body_btn.toggled.connect(self._phantom_switch)
    head_btn.toggled.connect(self._phantom_switch)
    body_btn.setChecked(True)

    phantom_layout = QVBoxLayout()
    phantom_layout.addWidget(phantom_lbl)
    phantom_layout.addWidget(body_btn)
    phantom_layout.addWidget(head_btn)
    # phantom_widget = QWidget()
    # phantom_widget.setLayout(phantom_layout)
    # phantom_widget.setMinimumWidth(75)

    main_layout = QHBoxLayout()
    main_layout.addLayout(grid)
    main_layout.addWidget(VSeparator())
    # main_layout.addStretch()
    main_layout.addLayout(phantom_layout)
    # main_layout.addStretch()

    self.setLayout(main_layout)
    self.setMaximumHeight(75)

  def setInfo(self, pat_info):
    name = pat_info['name'] if pat_info['name'] is not None else ''
    age = pat_info['age'][:3] if pat_info['age'] is not None else ''
    sex = pat_info['sex'] if pat_info['sex'] is not None else ''
    protocol = pat_info['protocol'] if pat_info['protocol'] is not None else ''
    date = pat_info['date'] if pat_info['date'] is not None else ''
    self.name_edit.setText(name)
    self.age_edit.setText(age)
    self.sex_edit.setText(sex)
    self.protocol_edit.setText(protocol)
    self.exam_date_edit.setText(date)

  def _phantom_switch(self):
    body_protocol = ['Chest', 'Liver', 'Liver to Kidney',
                    'Abdomen', 'Adrenal', 'Kidney', 
                    'Chest-Abdomen-Pelvis', 'Abdomen-Pelvis',
                    'Kidney to Bladder', 'Pelvis']
    head_protocol = ['Head', 'Head & Neck', 'Neck']
    sel = self.sender()
    level = 1 if self.first_run else 2
    self.first_run = False
    if sel.isChecked():
      with GetMainWindowProps(self, level) as par:
        par.tab3.protocol.clear()
        par.tab4.protocol.clear()
        if sel.text().lower() == 'body':
          par.tab3.protocol.addItems(body_protocol)
          par.tab4.protocol.addItems(body_protocol)
        else:
          par.tab3.protocol.addItems(head_protocol)
          par.tab4.protocol.addItems(head_protocol)
