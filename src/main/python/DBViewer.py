import sys
import os
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                             QTableView, QLabel, QPushButton, QLineEdit,
                             QHeaderView, QToolBar, QAction, QFileDialog,
                             QMessageBox)
from xlsxwriter.workbook import Workbook
import re

class DBViewer(QWidget):
  def __init__(self, ctx):
    super(DBViewer, self).__init__()
    self.ctx = ctx

    self.db = None
    self.layout = QVBoxLayout()
    self.queryModel = QSqlQueryModel()

    self.toolbar = QToolBar()
    self.tableView = QTableView()
    self.tableView.setModel(self.queryModel)

    self.exportXLS = QAction(self.ctx.export_icon, 'Export to Excel')
    self.totalPageLabel = QLabel()
    self.currentPageLabel = QLabel()
    self.switchPageLineEdit = QLineEdit()
    self.prevButton = QPushButton("Prev")
    self.nextButton = QPushButton("Next")
    self.refreshButton = QPushButton("Refresh")
    self.switchPageButton = QPushButton("Switch")
    self.currentPage = 1
    self.totalPage = None
    self.totalRecordCount = None
    self.pageRecordCount = 20

    self.initUI()
    self.openConnection()
    self.initModel()
    self.setUpConnect()
    self.updateStatus()

  def initUI(self):
    self.layout.setContentsMargins(11, 0, 11, 11)
    self.toolbar.addAction(self.exportXLS)
    self.layout.addWidget(self.toolbar)

    self.tableView.horizontalHeader().setStretchLastSection(True)
    self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.layout.addWidget(self.tableView)

    hLayout = QHBoxLayout()
    hLayout.addWidget(self.prevButton)
    hLayout.addWidget(self.nextButton)
    hLayout.addWidget(QLabel("Jump to Page:"))
    self.switchPageLineEdit.setFixedWidth(40)
    hLayout.addWidget(self.switchPageLineEdit)
    hLayout.addWidget(self.switchPageButton)
    hLayout.addStretch()
    hLayout.addWidget(QLabel("Page"))
    hLayout.addWidget(self.currentPageLabel)
    hLayout.addWidget(QLabel("of"))
    hLayout.addWidget(self.totalPageLabel)
    # hLayout.addStretch()
    hLayout.addWidget(self.refreshButton)
    

    self.layout.addLayout(hLayout)
    self.setLayout(self.layout)

    self.setWindowTitle("Patients Record")
    self.resize(960, 640)

  def setUpConnect(self):
    self.prevButton.clicked.connect(self.onPrevPage)
    self.nextButton.clicked.connect(self.onNextPage)
    self.switchPageButton.clicked.connect(self.onSwitchPage)
    self.refreshButton.clicked.connect(self.onRefresh)
    self.exportXLS.triggered.connect(self.onExport)

  def openConnection(self):
    PATIENTS_DB_PATH = self.ctx.patients_database()
    if self.db:
      self.onClose()
    self.db = QSqlDatabase.addDatabase("QSQLITE")
    self.db.setDatabaseName(PATIENTS_DB_PATH)
    if not self.db.open():
      return False

  def initModel(self):
    self.queryModel.setHeaderData(0, Qt.Horizontal, "ID")
    self.queryModel.setHeaderData(1, Qt.Horizontal, "Name")
    self.queryModel.setHeaderData(2, Qt.Horizontal, "Protocol_ID")
    self.queryModel.setHeaderData(3, Qt.Horizontal, "Protocol")
    self.queryModel.setHeaderData(4, Qt.Horizontal, "Date")
    self.queryModel.setHeaderData(5, Qt.Horizontal, "Age")
    self.queryModel.setHeaderData(6, Qt.Horizontal, "Sex_ID")
    self.queryModel.setHeaderData(7, Qt.Horizontal, "Sex")
    self.queryModel.setHeaderData(8, Qt.Horizontal, "CTDIVol")
    self.queryModel.setHeaderData(9, Qt.Horizontal, "DE_WED")
    self.queryModel.setHeaderData(10, Qt.Horizontal, "SSDE")
    self.queryModel.setHeaderData(11, Qt.Horizontal, "DLP")
    self.queryModel.setHeaderData(12, Qt.Horizontal, "DLPc")
    self.queryModel.setHeaderData(13, Qt.Horizontal, "Effective_Dose")
    
    # Query all records
    sql = "SELECT * FROM PATIENTS"
    self.queryModel.setQuery(sql, self.db)
    self.totalRecordCount = self.queryModel.rowCount()
    if self.totalRecordCount % self.pageRecordCount == 0:
      self.totalPage = int(self.totalRecordCount / self.pageRecordCount)
    else:
      self.totalPage = int(self.totalRecordCount / self.pageRecordCount) + 1

    # Show first page
    sql = f"SELECT * FROM PATIENTS LIMIT {0},{self.pageRecordCount:#d}"
    self.queryModel.setQuery(sql, self.db)

  def onExport(self):
    filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Workbook (*.xlsx)")
    if not filename:
      return
    workbook = Workbook(filename)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    sql = "SELECT * FROM PATIENTS"
    self.queryModel.setQuery(sql, self.db)

    for row in range(self.queryModel.rowCount()+1):
      for col in range(self.queryModel.record(row).count()):
        if row==0:
          worksheet.write(row, col, self.queryModel.record().fieldName(col), bold)
        else:
          worksheet.write(row, col, self.queryModel.record(row).value(col))
    workbook.close()
    QMessageBox.information(self, "Success", "Records can be found in "+filename+" .")

  def onRefresh(self):
    self.openConnection()
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
    szText = self.switchPageLineEdit.text()
    pattern = re.compile('^[0-9]+$')
    match = pattern.match(szText)
    if not match:
      QMessageBox.information(self, "Tips", "Please enter a number.")
      return
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
    self.queryModel.setQuery(sql)

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

  def onClose(self):
    PATIENTS_DB_PATH = self.ctx.patients_database()
    self.db.close()
    del self.db
    QSqlDatabase.removeDatabase(PATIENTS_DB_PATH)
    self.db = None

  def closeEvent(self, event):
    self.onClose()
    

# if __name__ == "__main__":
#   app = QApplication(sys.argv)
#   window = DBViewer()
#   window.show()
#   sys.exit(app.exec_())
