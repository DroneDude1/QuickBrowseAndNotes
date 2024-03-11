

from PyQt6 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebEngineCore
from PyQt6.QtCore import QUrl
import requests
import PyQt6.QtGui as QtGui
import pynput.keyboard as kb
import sys
import multiprocessing
import time
import os
import json

default_file = r"C:\Users\Maxed\PycharmProjects\QuickBrowse\QuickBrowse\note.txt"




def on_press(show, key):
    if str(key) == '<49>':
        with show.get_lock():
            show.value = 1
    elif str(key) == "key.esc":
        show.value = 2

def switch(show):
    with kb.Listener(on_press=lambda k: on_press(show, k)) as listener:
        listener.join()



def start_worker(show):
    p = multiprocessing.Process(target=switch, args=(show,))
    p.start()
    return p

def monitor_worker(show):
    p = start_worker(show)
    while True:
        if not p.is_alive():
            p = start_worker(show)
        time.sleep(0.2)

def on_text_input(text):
    print(text)


class MyLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None, function=None, textColor=None, backgroundColor=None):
        super(MyLineEdit, self).__init__(parent)
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        self.function = function
        self.parent_thing = parent

    def setUrlWidget(self, widget):
        self.urlWidget = widget

    def setButton(self, button):
        self.button = button

    def _setUrl(self, url):
        self.urlWidget.load(QUrl(self.function(url)))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self._setUrl(self.text())
            self.button.show()
            self.setStyleSheet(f"""
                        border: 1px solid grey;
                        border-top-left-radius: 10%;
                        border-top-right-radius: 10%;
                        border-bottom-right-radius: 0px;
                        border-bottom-left-radius: 0px;
                        border-bottom: 3px solid grey;
                        background-color: {self.backgroundColor.name()};
                        color: {self.textColor.name()};
                    """)
            self.urlWidget.show()
            self.activateWindow()
            event.accept()
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            with show.get_lock():
                show.value = 2
            event.accept()
        else:
            super(MyLineEdit, self).keyPressEvent(event)

    def external_load_url(self, url):
        print(url)
        try:
            self.urlWidget.load(QUrl(url))
        except:
            try:
                self.urlWidget.load(QUrl("http://www.google.com/search?q=" + self.function(url)))
            except:
                print("Load url failed")
        print("loaded")
        self.button.show()
        self.setStyleSheet(f"""
                    border: 1px solid grey;
                    border-top-left-radius: 10%;
                    border-top-right-radius: 10%;
                    border-bottom-right-radius: 0px;
                    border-bottom-left-radius: 0px;
                    border-bottom: 3px solid grey;
                    background-color: {self.backgroundColor.name()};
                    color: {self.textColor.name()};
                """)
        self.urlWidget.show()

class Dialog(QtWidgets.QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
    def keyPressEvent(self, event):
        if not event.key() == QtCore.Qt.Key.Key_Escape:
            super(Dialog).keyPressEvent(event)
        else:

            event.accept()

class button(QtWidgets.QPushButton):
    def __init__(self, text, parent):
        super().__init__(text, parent=parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            event.accept()
        elif not (event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter):
            super(button).keyPressEvent(event)

class textedit(QtWidgets.QTextEdit):
    def __init__(self, parent):
        super().__init__(parent=parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            with show.get_lock():
                show.value = 2
            event.accept()
        elif event.modifiers():
            event.accept()
        else:
            super(textedit).keyPressEvent(event)


class TextEditor(QtWidgets.QWidget):
    """
    This class is a simple text editor that allows you to open and save files. It will be the basis for the text editor which is not yet implemented.
    """
    def __init__(self, parent, textColor, backgroundColor):
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        self.file = default_file
        super().__init__(parent=parent)

        self.header_label = QtWidgets.QLabel(self)

        # Set the text for the label
        self.header_label.setText("Notepad")

        # Set the font size and weight for the label
        font = QtGui.QFont()
        font.setPointSize(parent.height()//100)  # Set the font size
        font.setBold(True)  # Set the font weight
        self.header_label.setFont(font)

        # Set the alignment for the label
        self.header_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.header_label.setGeometry(QtCore.QRect(0, 0, parent.width() // 3, parent.height() // 40))
        self.header_label.setStyleSheet("background: white;"
                                        "border: 1px solid grey;"
                                       "border-top-left-radius: 10%;"
                                        "border-top-right-radius: 10%;"
                                       "border-bottom: 2px solid grey;"f"background-color: {self.backgroundColor.name()};"
                                       f"color: {self.textColor.name()};")

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setStyleSheet(f"background-color: {self.backgroundColor.name()};"
                                     f"color: {self.textColor.name()};"
                                     "border: 1px solid grey;"
                                     )

        if self.file and self.file.endswith('.txt') and os.path.exists(self.file):
            with open(self.file, 'r') as file:
                self.text_edit.setText(file.read())

        self.open_button = button('Open', self)
        self.save_button = button('Save', self)

        self.header_label.setGeometry(QtCore.QRect(0, 0, parent.width() // 3, parent.height() // 40))
        self.open_button.setGeometry(QtCore.QRect(0, parent.height()//3, parent.width() // 6+1, parent.height() // 40))
        self.save_button.setGeometry(QtCore.QRect(parent.width() // 6+1, parent.height() // 3, parent.width() // 6, parent.height() // 40))
        self.text_edit.setGeometry(QtCore.QRect(0, parent.height() // 40, parent.width() // 3, parent.height() // 3 - parent.height() // 40))

        self.open_button.setStyleSheet("background: white;"
                                       "border: 1px solid grey;"
                                       "border-bottom-left-radius: 10%;"
                                       "border-top: 2px solid grey;"
                                       "border-right: 1px solid grey;"
                                       f"background-color: {self.backgroundColor.name()};"
                                       f"color: {self.textColor.name()};"
                                       )
        self.save_button.setStyleSheet("background: white;"
                                       "border: 1px solid grey;"
                                       "border-bottom-right-radius: 10%;"
                                       "border-top: 3px solid grey;"
                                       "border-left: 1px solid grey;"
                                       f"background-color: {self.backgroundColor.name()};"
                                       f"color: {self.textColor.name()};")


        self.open_button.clicked.connect(self.open_file)
        self.save_button.clicked.connect(self.save_file)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            with show.get_lock():
                show.value = 2

            event.accept()
        elif event.modifiers():
            event.accept()
        else:
            super(TextEditor).keyPressEvent(event)

    def open_file(self):
        file_name, module = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '', 'Text Files (*.txt);;All Files (*)')
        if file_name:
            with open(file_name, 'r') as file:
                self.text_edit.setText(file.read())

        self.text_edit.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.text_edit.setFocus()
        return

    def save_file(self):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'Text Files (*.txt);;All Files (*)')
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit.toPlainText())
        self.text_edit.setFocus()
        return

    def setGeometry(self, a0):
        self.open_button.setGeometry(QtCore.QRect(0, a0.height()//15 * 14, a0.width() // 2, a0.height() // 15))
        self.save_button.setGeometry(QtCore.QRect(a0.width() // 2, a0.height()//15 * 14 -1, a0.width() // 2, a0.height() // 15 + 1))
        self.text_edit.setGeometry(QtCore.QRect(0, a0.height() // 15, a0.width(), a0.height() // 15 * 13))

        self.header_label.setGeometry(QtCore.QRect(0, 0, a0.width(), a0.height() // 15))
        font = QtGui.QFont()
        font.setPointSize(a0.height() // 30)  # Set the font size
        font.setBold(True)  # Set the font weight
        self.header_label.setFont(font)
        self.open_button.setFont(font)
        self.save_button.setFont(font)
        super().setGeometry(a0)

class Search_Widget(QtWidgets.QWidget):
    def __init__(self, parent, function, textColor, backgroundColor):
        self.parent = parent
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        super().__init__(parent=parent)
        self.widget = QtWidgets.QWidget(parent=parent)
        self.widget.setGeometry(QtCore.QRect(0, 0, parent.width(), parent.height()))
        self.widget.setObjectName("widget")

        self.open_in_browser_button = button('Open in Browser', self.widget)
        self.open_in_browser_button.clicked.connect(self.open_in_browser)
        self.open_in_browser_button.hide()
        self.open_in_browser_button.setObjectName("open_in_browser_button")
        self.open_in_browser_button.setAutoFillBackground(True)

        self.lineEdit = MyLineEdit(parent=self.widget, function=function, textColor=self.textColor, backgroundColor=self.backgroundColor)
        self.lineEdit.setPlaceholderText("Search...")
        self.lineEdit.setGeometry(
            QtCore.QRect(3 * self.widget.width() // 24, self.widget.height() // 3 - self.widget.height() // 20,
                         self.widget.width() // 3, self.widget.height() // 20))

        self.open_in_browser_button.setGeometry(
            QtCore.QRect(3 * self.widget.width() // 24, 2 * self.widget.height() // 3,
                         self.widget.width() // 3, self.widget.height() // 20))

        self.open_in_browser_button.setStyleSheet(f"""
                        border-top-left-radius: 0%;
                        border-top-right-radius: 0%;
                        border-bottom-right-radius: 10px;
                        border-bottom-left-radius: 10px;
                        border: 1px solid grey;
                        border-top: 3px solid grey;
                        background-color: {backgroundColor.name()};
                        color: {textColor.name()};
                    """)
        self.open_in_browser_button.setFont(QtGui.QFont("Arial", self.widget.height()//70))

        self.lineEdit.setStyleSheet(f"""border-radius: 10%;
                                    border: 1px solid grey;
                                    background-color: {backgroundColor.name()};
                                    color: {textColor.name()};""")
        self.lineEdit.setFont(QtGui.QFont("Arial", self.widget.height()//50))

        self.lineEdit.setObjectName("lineEdit")
        self.webview = QtWebEngineWidgets.QWebEngineView(self.widget)




        android_user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Mobile Safari/537.36"
        profile = QtWebEngineCore.QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(android_user_agent)
        profile.setPersistentCookiesPolicy(QtWebEngineCore.QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        profile.setPersistentStoragePath("C:/Users/Maxed/AppData/Local/QtWebEngine/Default")

        page = QtWebEngineCore.QWebEnginePage(profile, parent=self.widget)

        self.webview.setPage(page)
        self.webview.setGeometry(
            QtCore.QRect(3 * self.widget.width() // 24, self.widget.height() // 3, self.widget.width() // 3,
                         self.widget.height() // 3))
        self.webview.load(QUrl("http://bing.com/"))
        self.webview.setObjectName("webview")
        self.webview.setStyleSheet(f"""background-color: {backgroundColor.name()};
                                    color: {textColor.name()};
                                    border: 1px solid grey;""")

        self.webview.hide()
        # Dialog.setCentralWidget(self.webview)

        self.lineEdit.setUrlWidget(self.webview)
        # Add a button to open the current URL in a browser

        self.lineEdit.setButton(self.open_in_browser_button)

    def open_in_browser(self):
        # Open the current URL in the default web browser
        if self.open_in_browser_button.underMouse():
            QtGui.QDesktopServices.openUrl(self.webview.url())
            with show.get_lock():
                show.value = 2

    def hide(self):
        super().hide()
        self.widget.hide()
        self.webview.hide()
        self.lineEdit.hide()
        self.open_in_browser_button.hide()




    def show(self):


        self.lineEdit.setStyleSheet(f"""border-radius: 10%;
                                    border: 1px solid grey;
                                    background-color: {self.backgroundColor.name()};
                                    color: {self.textColor.name()};""")
        self.lineEdit.show()
        self.widget.show()
        super().show()

    def keyPressEvent(self, event):
        if not event.key() == QtCore.Qt.Key.Key_Escape:
            super(Search_Widget).keyPressEvent(event)
        else:
            with show.get_lock():
                show.value = 2
            event.accept()

    def setGeometry(self, a0):
        self.widget.setGeometry(a0)

        self.open_in_browser_button.setGeometry(
            QtCore.QRect(0, a0.height()//15*14,
                         a0.width(), a0.height()//15))
        self.lineEdit.setGeometry(
            QtCore.QRect(0, 0,
                         a0.width(), int(1.5 * a0.height()//15)))
        self.webview.setGeometry(
            QtCore.QRect(0, int(1.5 * a0.height()//15), a0.width(),
                         int(a0.height()//15*12.5)))

        self.lineEdit.setFont(QtGui.QFont("Arial", self.lineEdit.height()//2))

        super().setGeometry(a0)

class URLWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, textColor=None, backgroundColor=None):
        super(URLWidget, self).__init__(parent)
        self.textColor = textColor
        self.backgroundColor = backgroundColor

    def setLineEdit(self, widget):
        self.lineEdit = widget

    def set_urls(self, urls, names):
        self.buttons = []
        for i, url in enumerate(zip(urls, names)):
            url, name = url
            button = QtWidgets.QPushButton(self)
            button.setText(name)
            button.setFont(QtGui.QFont("Arial", button.width() // len(name)))
            button.setGeometry(
                QtCore.QRect(0, self.height() // len(urls) * i + (self.height() // len(urls) - self.height() // (len(urls) + 1)) // len(urls) * i , self.width(), self.height() // (len(urls) + 1)))
            button.clicked.connect(lambda _, url_loop=url: self.lineEdit.external_load_url(url_loop))
            button.setStyleSheet(f"""
                                    border: 1px solid grey;
                                    border-radius: 10%;
                                    background-color: {self.backgroundColor.name()};
                                    color: {self.textColor.name()};
                                """)
            self.buttons.append(button)

    def setGeometry(self, a0):
        for i, button in enumerate(self.buttons):
            button.setGeometry(
                QtCore.QRect(0, a0.height() // len(self.buttons) * i + (
                            a0.height() // len(self.buttons) - a0.height() // (len(self.buttons) + 1)) // len(self.buttons) * i,
                             a0.width(), a0.height() // (len(self.buttons) + 1)))
            button.setFont(QtGui.QFont("Arial", button.width() // len(button.text())))

        super().setGeometry(a0)


class Ui_Dialog(object):
    def setupUi(self, Dialog:QtWidgets.QDialog, textColor, backgroundColor):
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        self.show = False
        self.Dialog = Dialog
        self.screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).availableGeometry()

        self.Dialog.setObjectName("Dialog")
        self.Dialog.resize(self.screen.width(), self.screen.height())
        self.Dialog.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.browser = Search_Widget(self.Dialog, lambda x: "http://bing.com/search?q=" + x.replace(" ", "+"), self.textColor, self.backgroundColor)
        self.notes = TextEditor(self.Dialog, self.textColor, self.backgroundColor)
        self.notes.setGeometry(
            QtCore.QRect(13 * self.screen.width() // 24, self.screen.height() // 3 - self.screen.height() // 20,
                         self.screen.width() // 3,
                         self.screen.height() // 2))
        self.browser.setGeometry(QtCore.QRect(3 * self.screen.width() // 24, self.screen.height() // 3 - self.screen.height() // 20, self.screen.width()//3, self.screen.height()//2))

         # Set the opacity to 50%
        self.urlWidget = URLWidget(self.Dialog, self.textColor, self.backgroundColor)
        self.urlWidget.set_urls(["https://www.desmos.com/calculator", "https://www.claude.ai", "https://www.youtube.com", "https://www.stackoverflow.com"], ["Desmos", "Claude", "Youtube", "Stack\nOverflow"])
        self.urlWidget.setGeometry(QtCore.QRect(23 * self.screen.width() // 48, self.screen.height() // 3 - self.screen.height() // 20, self.screen.width()//24, self.screen.height()//2))
        self.urlWidget.setLineEdit(self.browser.lineEdit)

        self.retranslateUi(self.Dialog)
        QtCore.QMetaObject.connectSlotsByName(self.Dialog)
        self.Dialog.show()
        self.Dialog.hide()
        self.browser.hide()
        self.notes.hide()
        self.Dialog.setWindowFlags(self.Dialog.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)

    def keyPressEvent(self, event):
        if not event.key() == QtCore.Qt.Key.Key_Escape:
            super(Ui_Dialog).keyPressEvent(event)
        else:
            event.accept()

        #keyboard.add_hotkey("esc", self.on_shortcut_activated)


    def on_shortcut_activated(self):
        self.show = not self.show
        if self.show:
            if self.screen != QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).availableGeometry():
                self.screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).availableGeometry()
                self.Dialog.setGeometry(self.screen)
                self.browser.setGeometry(
                    QtCore.QRect(3 * self.screen.width() // 24, self.screen.height() // 3 - self.screen.height() // 20,
                                 self.screen.width() // 3, self.screen.height() // 2))
                self.notes.setGeometry(
                    QtCore.QRect(13 * self.screen.width() // 24, self.screen.height() // 3 - self.screen.height() // 20,
                                 self.screen.width()//3,
                                 self.screen.height()//2))
                self.urlWidget.setGeometry(
                    QtCore.QRect(23 * self.screen.width() // 48, self.screen.height() // 3 - self.screen.height() // 20,
                                 self.screen.width() // 24, self.screen.height() // 2))

                self.retranslateUi(self.Dialog)
                self.Dialog.show()
                self.Dialog.hide()
                self.browser.hide()
                self.notes.hide()
                self.urlWidget.hide()

            self.browser.show()
            self.notes.show()
            self.urlWidget.show()
            self.Dialog.showFullScreen()
            self.Dialog.activateWindow()
            self.browser.lineEdit.setFocus()
        else:
            self.Dialog.hide()
            self.browser.hide()
            self.notes.hide()
            self.urlWidget.hide()


    def check_keyboard_queue(self, show):
        if show.value == 1:
            self.on_shortcut_activated()
            show.value = 0
        elif show.value == 2 and self.show:
            self.on_shortcut_activated()
            show.value = 0

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Quick Browse", "Quick Browse"))

def main():
    global show
    show = multiprocessing.Value('i', 0)
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()

    textColor = QtGui.QColor(255, 255, 255)
    backgroundColor = QtGui.QColor(50, 50, 50)

    ui.setupUi(Dialog, textColor, backgroundColor)



    keyboard_process = multiprocessing.Process(target=monitor_worker, args=(show,))

    keyboard_process.start()

    # Start a timer to check the queue every 100 ms
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: ui.check_keyboard_queue(show))
    timer.start(100)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

