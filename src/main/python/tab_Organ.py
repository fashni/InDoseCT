from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QScrollArea, QRadioButton, QButtonGroup, QCheckBox
from PyQt5.QtCore import Qt
from custom_widgets import HSeparator, VSeparator, Edit, Label, GetMainWindowProps

class OrganTab(QWidget):
  def __init__(self, *args, **kwargs):
    super(OrganTab, self).__init__(*args, **kwargs)
    self.initVar()
    self.initUI()

  def initVar(self):
    pass

  def initUI(self):
    prot_lbl = QLabel('Protocol:')
    self.protocol = QComboBox()
    self.calc_btn = QPushButton('Calculate')

    self.organs_edit = [QLineEdit('0') for i in range(28)]
    [organ_edit.setMaximumWidth(50) for organ_edit in self.organs_edit]

    grid = QGridLayout()
    grid.setHorizontalSpacing(0)
    grid.setVerticalSpacing(1)

    for col in range(2):
      for row in range(14):
        grid.addWidget(self.organs_edit[14*col+row], row, 2*col+1)

    grid.addWidget(Label(78, 'Marrow'), 0, 0)
    grid.addWidget(Label(78, 'Bones'), 1, 0)
    grid.addWidget(Label(78, 'Skin'), 2, 0)
    grid.addWidget(Label(78, 'Brain'), 3, 0)
    grid.addWidget(Label(78, 'Eyes'), 4, 0)
    grid.addWidget(Label(78, 'Larynx-Pharynx'), 5, 0)
    grid.addWidget(Label(78, 'Tyroid'), 6, 0)
    grid.addWidget(Label(78, 'Trachea-Bronchi'), 7, 0)
    grid.addWidget(Label(78, 'Esophagus'), 8, 0)
    grid.addWidget(Label(78, 'Lungs'), 9, 0)
    grid.addWidget(Label(78, 'Thymus'), 10, 0)
    grid.addWidget(Label(78, 'Breasts'), 11, 0)
    grid.addWidget(Label(78, 'Heart'), 12, 0)
    grid.addWidget(Label(78, 'Liver'), 13, 0)
    grid.addWidget(Label(78, 'Stomach'), 0, 2)
    grid.addWidget(Label(78, 'Spleen'), 1, 2)
    grid.addWidget(Label(78, 'Large Intestine'), 2, 2)
    grid.addWidget(Label(78, 'Adrenals'), 3, 2)
    grid.addWidget(Label(78, 'Pancreas'), 4, 2)
    grid.addWidget(Label(78, 'Small Intestine'), 5, 2)
    grid.addWidget(Label(78, 'Kidneys'), 6, 2)
    grid.addWidget(Label(78, 'Gallbladder'), 7, 2)
    grid.addWidget(Label(78, 'Ovaries'), 8, 2)
    grid.addWidget(Label(78, 'Uterus'), 9, 2)
    grid.addWidget(Label(78, 'Vagina'), 10, 2)
    grid.addWidget(Label(78, 'Bladder'), 11, 2)
    grid.addWidget(Label(78, 'Prostate'), 12, 2)
    grid.addWidget(Label(78, 'Testes'), 13, 2)

    main_layout = QVBoxLayout()
    main_layout.addWidget(prot_lbl)
    main_layout.addWidget(self.protocol)
    main_layout.addWidget(self.calc_btn)
    main_layout.addWidget(HSeparator())
    main_layout.addLayout(grid)
    main_layout.addStretch()

    self.setLayout(main_layout)
