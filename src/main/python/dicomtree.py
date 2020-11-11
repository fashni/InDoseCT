# dcm_qt_tree.py
"""View DICOM files in a tree using Qt and PySide"""
# Copyright (c) 2013 Padraig Looney
# This file is released under the
# pydicom (https://github.com/pydicom/pydicom)
# license, see the file LICENSE available at
# (https://github.com/pydicom/pydicom)

import pydicom
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QTreeView, QDialogButtonBox, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
import collections


class DicomTree(QDialog):
  def __init__(self, ds, *args, **kwargs):
    super(DicomTree, self).__init__()
    self.ds = ds
    self.initModel()
    self.initUI()
    self.sigConnect()

  def initUI(self):
    self.font = QFont('Courier', 8)
    self.setWindowTitle('DICOM Tree View')
    self.layout = QVBoxLayout()
    self.tree = QTreeView()
    self.tree.setFont(self.font)
    self.tree.setModel(self.model)

    btns = QDialogButtonBox.Close
    self.buttons = QDialogButtonBox(btns)

    self.layout.addWidget(self.tree)
    self.layout.addWidget(self.buttons)

    self.setLayout(self.layout)
    self.resize(960, 480)

  def initModel(self):
    self.ds.decode()
    self.model = self.ds_to_model(self.ds)

  def sigConnect(self):
    self.buttons.rejected.connect(self.reject)

  def ds_to_model(self, dic):
    model = QStandardItemModel()
    parentItem = model.invisibleRootItem()
    self.recurse_ds_to_item(dic, parentItem)
    return model

  def recurse_ds_to_item(self, ds, parent):
    for el in ds:
      item = QStandardItem(str(el))
      parent.appendRow(item)
      if el.VR == 'SQ':
        for i, dataset in enumerate(el.value):
          sq_item_description = el.name.replace(" Sequence", "")  # XXX not i18n
          item_text = QStandardItem("{0:s} {1:d}".format(sq_item_description, i + 1))
          item.appendRow(item_text)
          self.recurse_ds_to_item(dataset, item_text)

def main():
  filename = sys.argv[1]
  ds = pydicom.dcmread(filename)
  app = QApplication(sys.argv)
  dicomTree = DicomTree(ds)
  sys.exit(dicomTree.exec_())

if __name__ == "__main__":
  main()
