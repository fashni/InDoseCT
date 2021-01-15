from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QAbstractItemView, QIcon
from PyQt5.QtSql import QSqlQueryModel, QSqlTableModel
from PyQt5.QtWidgets import (QDesktopWidget, QDialog, QFileDialog, QHBoxLayout,
                             QMessageBox, QPushButton, QTableView, QToolBar,
                             QVBoxLayout)
from xlsxwriter.workbook import Workbook


class DBViewer(QDialog):
  resized = pyqtSignal(object)
  def __init__(self, ctx, par, *args, **kwargs):
    super(DBViewer, self).__init__(*args,**kwargs)
    self.setAttribute(Qt.WA_DeleteOnClose)
    self.setWindowFlags(self.windowFlags() |
                        Qt.WindowSystemMenuHint |
                        Qt.WindowMinMaxButtonsHint)
    self.ctx = ctx
    self.par = par
    self.layout = QVBoxLayout()
    self.query_model = QSqlQueryModel()

    self.toolbar = QToolBar()
    self.table_view = QTableView()
    self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

    self.export_excel = QPushButton(self.ctx.export_icon, 'Export to Excel',)
    self.refresh_btn = QPushButton("Refresh")
    self.close_btn = QPushButton("Close")
    self.delete_rows_btn = QPushButton("Delete Selected Row(s)")
    self.delete_rows_btn.setEnabled(False)

    self.initModel()
    self.initUI()
    self.sigConnect()

  def initUI(self):
    self.layout.setContentsMargins(11, 0, 11, 11)
    self.toolbar.addWidget(self.export_excel)
    self.layout.addWidget(self.toolbar)

    self.close_btn.setAutoDefault(True)
    self.close_btn.setDefault(True)
    self.refresh_btn.setAutoDefault(False)
    self.refresh_btn.setDefault(False)
    self.delete_rows_btn.setAutoDefault(False)
    self.delete_rows_btn.setDefault(False)
    self.export_excel.setAutoDefault(False)
    self.export_excel.setDefault(False)

    self.table_view.resizeColumnsToContents()
    self.layout.addWidget(self.table_view)

    hLayout = QHBoxLayout()
    hLayout.addWidget(self.delete_rows_btn)
    hLayout.addStretch()
    hLayout.addWidget(self.refresh_btn)
    hLayout.addWidget(self.close_btn)

    self.layout.addLayout(hLayout)
    self.setLayout(self.layout)

    self.setWindowTitle("Patients Record")
    wds = [self.table_view.columnWidth(c) for c in range(self.table_view.model().columnCount())]
    self.resize(sum(wds)+40, 600)
    rect = self.frameGeometry()
    rect.moveCenter(QDesktopWidget().availableGeometry().center())
    self.move(rect.topLeft().x(), rect.topLeft().y())

  def sigConnect(self):
    self.close_btn.clicked.connect(self.accept)
    self.refresh_btn.clicked.connect(self.on_refresh)
    self.delete_rows_btn.clicked.connect(self.on_delete_rows)
    self.export_excel.clicked.connect(self.on_export)
    self.resized.connect(self.on_window_resize)
    self.table_view.horizontalHeader().sectionResized.connect(self.on_column_resize)

  def initModel(self):
    self.table_model = QSqlTableModel(db=self.ctx.database.patient_db)
    self.table_model.setTable('patients')
    self.table_model.setEditStrategy(QSqlTableModel.OnFieldChange)
    self.table_model.select()
    self.table_view.setModel(self.table_model)
    self.table_view.selectionModel().selectionChanged.connect(self.on_rows_selected)

  def on_export(self):
    filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Workbook (*.xlsx)")
    if not filename:
      return
    workbook = Workbook(filename)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    sql = "SELECT * FROM PATIENTS"
    self.query_model.setQuery(sql, self.ctx.database.patient_db)

    for row in range(self.query_model.rowCount()+1):
      for col in range(self.query_model.record(row).count()):
        if row==0:
          worksheet.write(row, col, self.query_model.record().fieldName(col), bold)
        worksheet.write(row+1, col, self.query_model.record(row).value(col))
    workbook.close()
    QMessageBox.information(self, "Success", "Records can be found in "+filename+" .")

  def on_refresh(self):
    self.initModel()

  def on_column_resize(self, id, oldsize, size):
    width = self.size().width()
    self.column_ratio[id] = size/width

  def on_window_resize(self, event):
    old_width = event.oldSize().width()
    width = event.size().width()
    if old_width == -1:
      self.column_ratio = [self.table_view.columnWidth(c)/width for c in range(self.table_view.model().columnCount())]
    else:
      self.table_view.horizontalHeader().sectionResized.disconnect(self.on_column_resize)
      [self.table_view.setColumnWidth(c, r*width) for c, r in enumerate(self.column_ratio)]
      self.table_view.horizontalHeader().sectionResized.connect(self.on_column_resize)

  def on_rows_selected(self):
    self.selected_rows = sorted(set(index.row() for index in self.table_view.selectedIndexes()))
    print(self.selected_rows)
    self.delete_rows_btn.setEnabled(len(self.selected_rows)!=0)

  def on_delete_rows(self):
    result = []
    for row in self.selected_rows:
      res = self.table_model.removeRow(row)
      result.append(res)
    if not all(result):
      print(self.table_model.lastError())
    self.ctx.records_count -= len(self.selected_rows)
    self.delete_rows_btn.setEnabled(False)
    self.on_refresh()
    self.par.info_panel.no_edit.setText(str(self.ctx.records_count + 1))

  def resizeEvent(self, event):
    self.resized.emit(event)
    return super(DBViewer, self).resizeEvent(event)
