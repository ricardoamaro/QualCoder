# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dialog_manage_links.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_manage_links(object):
    def setupUi(self, Dialog_manage_links):
        Dialog_manage_links.setObjectName("Dialog_manage_links")
        Dialog_manage_links.resize(794, 560)
        self.gridLayout = QtWidgets.QGridLayout(Dialog_manage_links)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(Dialog_manage_links)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 3, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(Dialog_manage_links)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 10))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 10))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)
        self.label_1 = QtWidgets.QLabel(Dialog_manage_links)
        self.label_1.setObjectName("label_1")
        self.gridLayout.addWidget(self.label_1, 2, 0, 1, 1)

        self.retranslateUi(Dialog_manage_links)
        QtCore.QMetaObject.connectSlotsByName(Dialog_manage_links)

    def retranslateUi(self, Dialog_manage_links):
        _translate = QtCore.QCoreApplication.translate
        Dialog_manage_links.setWindowTitle(_translate("Dialog_manage_links", "Manage file links"))
        self.label_1.setText(_translate("Dialog_manage_links", "Click on the file name to browse to the file. Or double-click to type in the new path."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_manage_links = QtWidgets.QDialog()
    ui = Ui_Dialog_manage_links()
    ui.setupUi(Dialog_manage_links)
    Dialog_manage_links.show()
    sys.exit(app.exec_())
