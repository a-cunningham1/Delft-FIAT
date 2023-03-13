/********************************************************************************
** Form generated from reading UI file 'ui_fiat.ui'
**
** Created by: Qt User Interface Compiler version 5.15.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_UI_FIAT_H
#define UI_UI_FIAT_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_ui_fiatClass
{
public:
    QMenuBar *menuBar;
    QToolBar *mainToolBar;
    QWidget *centralWidget;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *ui_fiatClass)
    {
        if (ui_fiatClass->objectName().isEmpty())
            ui_fiatClass->setObjectName(QString::fromUtf8("ui_fiatClass"));
        ui_fiatClass->resize(600, 400);
        menuBar = new QMenuBar(ui_fiatClass);
        menuBar->setObjectName(QString::fromUtf8("menuBar"));
        ui_fiatClass->setMenuBar(menuBar);
        mainToolBar = new QToolBar(ui_fiatClass);
        mainToolBar->setObjectName(QString::fromUtf8("mainToolBar"));
        ui_fiatClass->addToolBar(mainToolBar);
        centralWidget = new QWidget(ui_fiatClass);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        ui_fiatClass->setCentralWidget(centralWidget);
        statusBar = new QStatusBar(ui_fiatClass);
        statusBar->setObjectName(QString::fromUtf8("statusBar"));
        ui_fiatClass->setStatusBar(statusBar);

        retranslateUi(ui_fiatClass);

        QMetaObject::connectSlotsByName(ui_fiatClass);
    } // setupUi

    void retranslateUi(QMainWindow *ui_fiatClass)
    {
        ui_fiatClass->setWindowTitle(QCoreApplication::translate("ui_fiatClass", "ui_fiat", nullptr));
    } // retranslateUi

};

namespace Ui {
    class ui_fiatClass: public Ui_ui_fiatClass {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_UI_FIAT_H
