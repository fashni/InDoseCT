import sys
import os
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                             QTableView, QLabel, QPushButton, QLineEdit,
                             QHeaderView, QToolBar, QAction, QFileDialog,
                             QMessageBox, QDesktopWidget)
from xlsxwriter.workbook import Workbook

class DBViewer(QWidget):
  resized = pyqtSignal(object)
  def __init__(self, ctx):
    super(DBViewer, self).__init__()
    self.ctx = ctx

    self.layout = QVBoxLayout()
    self.queryModel = QSqlQueryModel()

    self.toolbar = QToolBar()
    self.tableView = QTableView()
    self.tableView.setModel(self.queryModel)

    self.exportXLS = QPushButton(self.ctx.export_icon, 'Export to Excel',)
    self.totalPageLabel = QLabel()
    self.currentPageLabel = QLabel()
    self.switchPageLineEdit = QLineEdit()
    self.switchPageLineEdit.tag = 'edit'
    self.prevButton = QPushButton("Prev")
    self.nextButton = QPushButton("Next")
    self.refreshButton = QPushButton("Refresh")
    self.switchPageButton = QPushButton("Jump to page")
    self.switchPageButton.tag = 'button'
    self.currentPage = 1
    self.totalPage = None
    self.totalRecordCount = None
    self.pageRecordCount = 20

    self.initModel()
    self.initUI()
    self.setUpConnect()
    self.updateStatus()

  def initUI(self):
    self.switchPageLineEdit.setValidator(QIntValidator())
    self.layout.setContentsMargins(11, 0, 11, 11)
    self.toolbar.addWidget(self.exportXLS)
    self.layout.addWidget(self.toolbar)

    self.tableView.resizeColumnsToContents()
    self.layout.addWidget(self.tableView)

    hLayout = QHBoxLayout()
    hLayout.addWidget(self.prevButton)
    hLayout.addWidget(self.nextButton)
    self.switchPageLineEdit.setFixedWidth(40)
    hLayout.addWidget(self.switchPageLineEdit)
    hLayout.addWidget(self.switchPageButton)
    hLayout.addStretch()
    hLayout.addWidget(QLabel("Page"))
    hLayout.addWidget(self.currentPageLabel)
    hLayout.addWidget(QLabel("of"))
    hLayout.addWidget(self.totalPageLabel)
    hLayout.addWidget(self.refreshButton)

    self.layout.addLayout(hLayout)
    self.setLayout(self.layout)

    self.setWindowTitle("Patients Record")
    wds = [self.tableView.columnWidth(c) for c in range(self.tableView.model().columnCount())]
    self.resize(sum(wds)+40, 600)
    rect = self.frameGeometry()
    rect.moveCenter(QDesktopWidget().availableGeometry().center())
    self.move(rect.topLeft().x(), rect.topLeft().y())

  def setUpConnect(self):
    self.prevButton.clicked.connect(self.onPrevPage)
    self.nextButton.clicked.connect(self.onNextPage)
    self.switchPageButton.clicked.connect(self.onSwitchPage)
    self.switchPageLineEdit.editingFinished.connect(self.onSwitchPage)
    self.refreshButton.clicked.connect(self.onRefresh)
    self.exportXLS.clicked.connect(self.onExport)
    self.resized.connect(self.on_window_resize)
    self.tableView.horizontalHeader().sectionResized.connect(self.on_column_resize)

  def initModel(self):
    # Query all records
    sql = "SELECT * FROM PATIENTS"
    self.queryModel.setQuery(sql, self.ctx.database.patient_db)
    self.totalRecordCount = self.queryModel.rowCount()
    if self.totalRecordCount % self.pageRecordCount == 0:
      self.totalPage = int(self.totalRecordCount / self.pageRecordCount)
    else:
      self.totalPage = int(self.totalRecordCount / self.pageRecordCount) + 1

    # Show first page
    sql = f"SELECT * FROM PATIENTS LIMIT {0},{self.pageRecordCount:#d}"
    self.queryModel.setQuery(sql, self.ctx.database.patient_db)

  def onExport(self):
    filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Workbook (*.xlsx)")
    if not filename:
      return
    workbook = Workbook(filename)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    sql = "SELECT * FROM PATIENTS"
    self.queryModel.setQuery(sql, self.ctx.database.patient_db)

    for row in range(self.queryModel.rowCount()+1):
      for col in range(self.queryModel.record(row).count()):
        if row==0:
          worksheet.write(row, col, self.queryModel.record().fieldName(col), bold)
        worksheet.write(row+1, col, self.queryModel.record(row).value(col))
    workbook.close()
    QMessageBox.information(self, "Success", "Records can be found in "+filename+" .")

  def onRefresh(self):
    self.initModel()
    if self.totalPage < self.currentPage:
      self.currentPage = 1
    limitIndex = (self.currentPage - 1) * self.pageRecordCount
    self.queryRecord(limitIndex)
    self.updateStatus()

  def onPrevPage(self):
    self.currentPage -= 1
    limitIndex = (self.currentPage - 1) * self.pageRecordCount
    self.queryRecord(limitIndex)
    self.updateStatus()

  def onNextPage(self):
    self.currentPage += 1
    limitIndex = (self.currentPage - 1) * self.pageRecordCount
    self.queryRecord(limitIndex)
    self.updateStatus()

  def onSwitchPage(self):
    sender = self.sender()
    if sender.tag == 'edit' and not self.switchPageLineEdit.hasFocus():
      return
    szText = self.switchPageLineEdit.text()
    if szText == "":
      QMessageBox.information(self, "Tips", "Please enter a page number.")
      return
    pageIndex = int(szText)
    if pageIndex > self.totalPage or pageIndex < 1:
      QMessageBox.information(self, "Tips", "No page specified.")
      return

    limitIndex = (pageIndex - 1) * self.pageRecordCount
    self.queryRecord(limitIndex)
    self.currentPage = pageIndex
    self.updateStatus()

  # Query records based on paging
  def queryRecord(self, limitIndex):
    sql = f"SELECT * FROM PATIENTS LIMIT {limitIndex:#d},{self.pageRecordCount:#d}"
    self.queryModel.setQuery(sql, self.ctx.database.patient_db)

  # Update buttons
  def updateStatus(self):
    self.currentPageLabel.setText(str(self.currentPage))
    self.totalPageLabel.setText(str(self.totalPage))
    if self.currentPage <= 1:
      self.prevButton.setEnabled(False)
    else:
      self.prevButton.setEnabled(True)

    if self.currentPage >= self.totalPage:
      self.nextButton.setEnabled(False)
    else:
      self.nextButton.setEnabled(True)

  def on_column_resize(self, id, oldsize, size):
    width = self.size().width()
    self.column_ratio[id] = size/width

  def on_window_resize(self, event):
    old_width = event.oldSize().width()
    width = event.size().width()
    if old_width == -1:
      self.column_ratio = [self.tableView.columnWidth(c)/width for c in range(self.tableView.model().columnCount())]
    else:
      self.tableView.horizontalHeader().sectionResized.disconnect(self.on_column_resize)
      [self.tableView.setColumnWidth(c, r*width) for c, r in enumerate(self.column_ratio)]
      self.tableView.horizontalHeader().sectionResized.connect(self.on_column_resize)

  def resizeEvent(self, event):
    self.resized.emit(event)
    return super(DBViewer, self).resizeEvent(event)
