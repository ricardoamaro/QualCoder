# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dialog_text_mining.ui'
#
# Created: Mon Feb 12 09:56:13 2018
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog_text_mining(object):
    def setupUi(self, Dialog_text_mining):
        Dialog_text_mining.setObjectName("Dialog_text_mining")
        Dialog_text_mining.setWindowModality(QtCore.Qt.NonModal)
        Dialog_text_mining.resize(1129, 715)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog_text_mining)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Dialog_text_mining)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 120))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 120))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.pushButton_export_selected = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_export_selected.setGeometry(QtCore.QRect(910, 20, 161, 30))
        self.pushButton_export_selected.setObjectName("pushButton_export_selected")
        self.pushButton_search = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_search.setGeometry(QtCore.QRect(730, 20, 131, 31))
        self.pushButton_search.setObjectName("pushButton_search")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10, 30, 61, 22))
        self.label_2.setObjectName("label_2")
        self.comboBox_coders = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_coders.setGeometry(QtCore.QRect(90, 20, 221, 34))
        self.comboBox_coders.setObjectName("comboBox_coders")
        self.radioButton_files = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_files.setGeometry(QtCore.QRect(10, 60, 102, 22))
        self.radioButton_files.setChecked(True)
        self.radioButton_files.setObjectName("radioButton_files")
        self.radioButton_cases = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_cases.setGeometry(QtCore.QRect(160, 60, 102, 22))
        self.radioButton_cases.setObjectName("radioButton_cases")
        self.radioButton_files_coded = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_files_coded.setGeometry(QtCore.QRect(10, 90, 151, 22))
        self.radioButton_files_coded.setObjectName("radioButton_files_coded")
        self.radioButton_cases_coded = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_cases_coded.setGeometry(QtCore.QRect(160, 90, 161, 22))
        self.radioButton_cases_coded.setObjectName("radioButton_cases_coded")
        self.comboBox_analysis = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_analysis.setGeometry(QtCore.QRect(420, 20, 261, 33))
        self.comboBox_analysis.setObjectName("comboBox_analysis")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(340, 27, 71, 20))
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.groupBox)
        self.label_selections = QtWidgets.QLabel(Dialog_text_mining)
        self.label_selections.setMinimumSize(QtCore.QSize(0, 60))
        self.label_selections.setMaximumSize(QtCore.QSize(16777213, 50))
        self.label_selections.setScaledContents(True)
        self.label_selections.setWordWrap(True)
        self.label_selections.setObjectName("label_selections")
        self.verticalLayout.addWidget(self.label_selections)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog_text_mining)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.groupBox_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tableWidget = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.treeWidget = QtWidgets.QTreeWidget(self.splitter)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.textEdit = QtWidgets.QTextEdit(self.splitter)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(Dialog_text_mining)
        QtCore.QMetaObject.connectSlotsByName(Dialog_text_mining)
        Dialog_text_mining.setTabOrder(self.comboBox_coders, self.pushButton_search)
        Dialog_text_mining.setTabOrder(self.pushButton_search, self.pushButton_export_selected)
        Dialog_text_mining.setTabOrder(self.pushButton_export_selected, self.textEdit)

    def retranslateUi(self, Dialog_text_mining):
        _translate = QtCore.QCoreApplication.translate
        Dialog_text_mining.setWindowTitle(_translate("Dialog_text_mining", "Text Mining"))
        self.pushButton_export_selected.setText(_translate("Dialog_text_mining", "Export selected file"))
        self.pushButton_search.setText(_translate("Dialog_text_mining", "Analyse"))
        self.label_2.setText(_translate("Dialog_text_mining", "Coder:"))
        self.radioButton_files.setText(_translate("Dialog_text_mining", "Files"))
        self.radioButton_cases.setText(_translate("Dialog_text_mining", "Cases"))
        self.radioButton_files_coded.setText(_translate("Dialog_text_mining", "Files coded"))
        self.radioButton_cases_coded.setText(_translate("Dialog_text_mining", "Cases coded"))
        self.label.setText(_translate("Dialog_text_mining", "Analysis"))
        self.label_selections.setText(_translate("Dialog_text_mining", "Analysis selections:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_text_mining = QtWidgets.QDialog()
    ui = Ui_Dialog_text_mining()
    ui.setupUi(Dialog_text_mining)
    Dialog_text_mining.show()
    sys.exit(app.exec_())

