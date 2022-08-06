# from ConfigUI import ConfigUI
# from PyQt5 import QtWidgets

# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = ConfigUI()
#     ui.setupUi(MainWindow)
#     MainWindow.show()
#     sys.exit(app.exec_())

from aqt import mw
from aqt.qt import QAction, QMenu, QKeySequence
from aqt.utils import showInfo, showWarning, tooltip, askUser

from .ConfigWrapper import ConfigWrapper

def profileHook():
    """
    Check username
    Check season
    """
    pass

def deleteHook():
    """
    Create backup
    """
    pass

def add_menu(Name, Button, exe, *sc):
	action = QAction(Button, mw)
	action.triggered.connect(exe)
	if not hasattr(mw, 'menu'):
		mw.menu = {}
	if Name not in mw.menu:
		add = QMenu(Name, mw)
		mw.menu[Name] = add
		mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(), add)
	mw.menu[Name].addAction(action)
	for i in sc:
		action.setShortcut(QKeySequence(i))

def invoke_setup():
	mw.lb_setup = ConfigWrapper()
	mw.lb_setup.show()
	mw.lb_setup.focus_on_me()

def config_setup():
	s = ConfigWrapper()
	if s.exec():
		pass

try:
	from aqt import gui_hooks
	gui_hooks.profile_did_open.append(profileHook)
	try:
		# this hook will be implemented in Anki 2.1.45
		gui_hooks.addons_dialog_will_delete_addons.append(deleteHook)
	except:
		print("addons_dialog_will_delete_addon is not a hook yet")
except:
    pass
	# config = mw.addonManager.getConfig(__name__)
	# if config["import_error"] == True:
	# 	showInfo("Because you're using an older Anki version some features of the Leaderboard add-on can't be used.", title="Leaderboard")
		# write_config("import_error", False)

add_menu('&AnkiVN',"&Config", invoke_setup)
#mw.addonManager.setConfigAction(__name__, config_setup)