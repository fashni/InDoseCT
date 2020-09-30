import sys
import json
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QPushButton, QLineEdit, QFileDialog,
                             QMessageBox, QTabWidget, QDialog, QDialogButtonBox,
                            )
from db import create_patients_table

class AppConfig(QDialog):
  def __init__(self, ctx):
    super(AppConfig, self).__init__()
    self.ctx = ctx

    btns = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Cancel
    self.buttons = QDialogButtonBox(btns)

    self.setWindowTitle("Settings")
    self.layout = QVBoxLayout()
    self.tabs = QTabWidget()
    self.setTabs()

    try:
      self.configs = self._get_config()
    except:
      self._set_default()

    self.layout.addWidget(self.tabs)
    self.layout.addWidget(self.buttons)
    
    self.patients_db.setText(os.path.abspath(self.configs['patients_db']))
    self.setLayout(self.layout)
    self.resize(400, 300)

  def setConnect(self):
    self.buttons.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.on_restore)
    self.buttons.accepted.connect(self.on_save)
    self.buttons.rejected.connect(self.reject)
    self.open_db.clicked.connect(self.on_open)

  def setTabs(self):
    self.db_tab = QWidget()
    grid = QVBoxLayout()

    h = QHBoxLayout()
    pr_label = QLabel('Patients Records Database:')
    self.patients_db = QLineEdit()
    self.patients_db.setMinimumWidth(400)
    self.open_db = QPushButton(self.ctx.save_icon, '')

    h.addWidget(self.patients_db)
    h.addWidget(self.open_db)
    h.addStretch()

    grid.addWidget(pr_label)
    grid.addLayout(h)
    grid.addStretch()

    self.db_tab.setLayout(grid)
    self.tabs.addTab(self.db_tab, 'Database')

    self.setConnect()

  def _get_config(self):
    with open(self.ctx.config_file(), 'r') as f:
      return json.load(f)
  
  def _set_config(self):
    with open(self.ctx.config_file(), 'w') as f:
      json.dump(self.configs, f, sort_keys=True, indent=4)

  def _set_default(self):
    self.configs = {
      'patients_db': self.ctx.default_patients_database,
    }
    self._set_config()
    self.patients_db.setText(os.path.abspath(self.configs['patients_db']))

  def on_save(self):
    self.configs['patients_db'] = os.path.abspath(self.patients_db.text())
    self._set_config()

    if not os.path.isfile(self.configs['patients_db']):
      create_patients_table(self.configs['patients_db'])
    self.accept()

  def on_open(self):
    filename, _ = QFileDialog.getSaveFileName(self, "Select Database File", os.path.join(self.configs['patients_db'], os.pardir), "Database (*.db)")
    print(filename)
    if not filename:
      return
    self.patients_db.setText(os.path.abspath(filename))

  def on_restore(self):
    btn_reply = QMessageBox.question(self, 'Restore Default', 'Restore the default settings?')
    if btn_reply == QMessageBox.No:
      return
    self._set_default()
    self.accept()


# if __name__ == "__main__":
#   app = QApplication(sys.argv)
#   window = AppConfig()
#   window.show()
#   sys.exit(app.exec_())
  