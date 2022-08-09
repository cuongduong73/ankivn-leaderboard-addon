from datetime import datetime
import json
from aqt import mw
from aqt.qt import QDialog, qtmajor
from aqt.utils import tooltip, showInfo, showWarning, askUser

if qtmajor > 5:
    from .pyqt6UI import config, forgot_password, register, change_password
    from PyQt6 import QtCore
else:
    from .pyqt5UI import config, forgot_password, register, change_password
    from PyQt5 import QtCore

from .. import version
from ..manager.season import LeagueSeason

CONFIG_KEY_USER = "username"
CONFIG_KEY_PASS = "password"
CONFIG_KEY_TOKEN = "token"
CONFIG_KEY_AUTHTOKEN = "authToken"
CONFIG_KEY_HOMESCREEN = "homescreen"
CONFIG_KEY_AUTOSYNC = "autosync"
CONFIG_KEY_SYNC_INT = "sync_interval"
CONFIG_KEY_MAXUSER = "max_users"
CONFIG_KEY_FOCUS = "focus_on_user"
CONFIG_KEY_MEDAL = "show_medals"


# NOTE: For testing only
season_start = datetime(2022, 8, 1, 0, 0, 0)
season_end = datetime(2022, 8, 30, 0, 0, 0)
new_day = 4
min_study_constraint = 20
############ End testing data #############


class ConfigWrapper(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.dialog_ui = config.Ui_ConfigDialog()
        self.manager = LeagueSeason(1)
        self._is_signin = False
        self._config = ConfigWrapper.get_config()
        self.dialog_ui.setupUi(self)
        self.setupUI()
        self.connect_signals_slots()

        # NOTE: For testing
        self.manager.set_stats_new_day(new_day)
        self.manager.set_stats_constraint(min_study_constraint)
        self.manager.set_stats_season_time(season_start, season_end)

    def setupUI(self):
        self.setWindowTitle(
            'AnkiVN Leaderboard Configuration - v{}'.format(version.__version__))
        self.dialog_ui.le_user.setText(
            ConfigWrapper.get_config_by_name(CONFIG_KEY_USER, self._config))
        self.dialog_ui.le_password.setText(
            ConfigWrapper.get_config_by_name(CONFIG_KEY_PASS, self._config))
        self.dialog_ui.cb_show_medal.setChecked(
            ConfigWrapper.get_config_by_name(CONFIG_KEY_MEDAL, self._config))

        is_autosync = ConfigWrapper.get_config_by_name(
            CONFIG_KEY_AUTOSYNC, self._config)
        self.dialog_ui.cb_autosync.setChecked(is_autosync)
        self.dialog_ui.sp_sync_minutes.setValue(
            ConfigWrapper.get_config_by_name(CONFIG_KEY_SYNC_INT, self._config))

        is_show_leaderboard = ConfigWrapper.get_config_by_name(
            CONFIG_KEY_HOMESCREEN, self._config)
        self.dialog_ui.cb_show_leaderboard.setChecked(is_show_leaderboard)
        self.dialog_ui.cb_focus_user.setChecked(
            ConfigWrapper.get_config_by_name(CONFIG_KEY_FOCUS, self._config))
        self.dialog_ui.sp_user_count.setValue(
            ConfigWrapper.get_config_by_name(CONFIG_KEY_MAXUSER, self._config))

        self.dialog_ui.sp_sync_minutes.setEnabled(is_autosync)
        self.dialog_ui.cb_focus_user.setEnabled(is_show_leaderboard)
        self.dialog_ui.sp_user_count.setEnabled(is_show_leaderboard)
        self._update_auth_btn()

    def connect_signals_slots(self):
        self.dialog_ui.btn_sync.released.connect(self._on_sync)
        self.dialog_ui.btn_save.released.connect(self._on_save)
        self.dialog_ui.btn_cancel.released.connect(self._on_cancel)
        self.dialog_ui.btn_sign.released.connect(self._on_sign)
        self.dialog_ui.btn_reset.released.connect(self._on_reset)
        self.dialog_ui.cb_show_leaderboard.stateChanged.connect(
            self._on_cb_show_leaderboard)
        self.dialog_ui.cb_autosync.stateChanged.connect(self._on_cb_autosync)

    def show_status(self, msg):
        self.dialog_ui.lbl_status.setText(msg)

    def focus_on_me(self):
        self.raise_()
        self.activateWindow()

    def _update_auth_btn(self):
        if(self._is_signin):
            self.dialog_ui.btn_sign.setText("Sign out")
            self.dialog_ui.btn_reset.setText("Change password")
            self.dialog_ui.le_password.setEnabled(False)
            self.dialog_ui.le_user.setEnabled(False)
            user = self.dialog_ui.le_user.text()
            msg = "Signed in with username {}!".format(user)
            self.show_status(msg)
        else:
            self.dialog_ui.btn_sign.setText("Sign in")
            self.dialog_ui.btn_reset.setText("Forgot")
            self.dialog_ui.le_password.setEnabled(True)
            self.dialog_ui.le_user.setEnabled(True)
            user = self.dialog_ui.le_user.text()
            msg = "Not signed in yet !"
            self.show_status(msg)

    ### Slots ###
    def _on_cb_show_leaderboard(self, state):
        self.dialog_ui.cb_focus_user.setEnabled(state)
        self.dialog_ui.sp_user_count.setEnabled(state)

    def _on_cb_autosync(self, state):
        self.dialog_ui.sp_sync_minutes.setEnabled(state)

    def _on_sign(self):
        # TODO: handle register when server reponse user not existed !
        user = self.dialog_ui.le_user.text()
        passwd = self.dialog_ui.le_password.text()
        if not self._is_signin:
            # Validate user and password
            if user == "" or passwd == "":
                msg = "Invalid user & password !"
                showWarning(msg)
                return
            else:
                self._is_signin = True
        else:
            self._is_signin = False

        self._update_auth_btn()

    def _on_reset(self):

        # Handle reset password case
        if self._is_signin:
            self.change_password_dialog = QDialog()
            self.change_password_dialog_ui = change_password.Ui_Dialog()
            self.change_password_dialog_ui.setupUi(self.change_password_dialog)
            self.change_password_dialog_ui.buttonBox.accepted.connect(
                self._on_dialog_change_password_accept)
            self.change_password_dialog_ui.buttonBox.rejected.connect(
                self._on_dialog_change_password_reject)
            self.change_password_dialog.show()

        # Handle forgot password case
        else:
            self.forgot_password_dialog = QDialog()
            self.forgot_password_dialog_ui = forgot_password.Ui_Dialog()
            self.forgot_password_dialog_ui.setupUi(self.forgot_password_dialog)
            self.forgot_password_dialog_ui.buttonBox.accepted.connect(
                self._on_dialog_forgot_password_accept)
            self.forgot_password_dialog_ui.buttonBox.accepted.connect(
                self._on_dialog_forgot_password_reject)
            self.forgot_password_dialog.show()

    def _on_sync(self):
        daily_stats = self.manager.get_user_today_stats().to_json()
        season_stats = self.manager.get_user_season_stats().to_json()

        showInfo(json.dumps(daily_stats))
        showInfo(json.dumps(season_stats))

    def _on_save(self):
        self._config[CONFIG_KEY_USER] = self.dialog_ui.le_user.text()
        self._config[CONFIG_KEY_PASS] = self.dialog_ui.le_password.text()
        self._config[CONFIG_KEY_FOCUS] = self.dialog_ui.cb_focus_user.isChecked()
        self._config[CONFIG_KEY_AUTOSYNC] = self.dialog_ui.cb_autosync.isChecked()
        self._config[CONFIG_KEY_HOMESCREEN] = self.dialog_ui.cb_show_leaderboard.isChecked()
        self._config[CONFIG_KEY_MAXUSER] = self.dialog_ui.sp_user_count.value()
        self._config[CONFIG_KEY_MEDAL] = self.dialog_ui.cb_show_medal.isChecked()
        self._config[CONFIG_KEY_SYNC_INT] = self.dialog_ui.sp_sync_minutes.value()
        ConfigWrapper.write_config(self._config)
        self.close()

    def _on_cancel(self):
        self.close()

    def _on_dialog_change_password_accept(self):
        old = self.change_password_dialog_ui.le_oldpass.text()
        new = self.change_password_dialog_ui.le_oldpass.text()
        confirm = self.change_password_dialog_ui.le_confirmpass.text()

        if new != confirm:
            showWarning("Password is not matched ! Please check again.")
        else:
            # TODO: Handle reset password
            pass

        self.change_password_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    def _on_dialog_change_password_reject(self):
        self.change_password_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    def _on_dialog_forgot_password_accept(self):
        email = self.forgot_password_dialog_ui.le_email.text()
        # TODO: Handle forgot password

        showInfo("We'll send you a email to reset your password if your email was already in our system !<br>Please check spam folder also")
        self.forgot_password_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    def _on_dialog_forgot_password_reject(self):
        self.forgot_password_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    ### Static methods ###
    @staticmethod
    def write_config(config: dict):
        mw.addonManager.writeConfig(__name__, config)

    @staticmethod
    def get_config():
        return mw.addonManager.getConfig(__name__)

    @staticmethod
    def write_config_by_name(name, value):
        config = ConfigWrapper.get_config()
        config_content = {
            CONFIG_KEY_USER: config[CONFIG_KEY_USER],
            CONFIG_KEY_PASS: config[CONFIG_KEY_PASS],
            CONFIG_KEY_TOKEN: config[CONFIG_KEY_TOKEN],
            CONFIG_KEY_AUTHTOKEN: config[CONFIG_KEY_AUTHTOKEN],
            CONFIG_KEY_HOMESCREEN: config[CONFIG_KEY_HOMESCREEN],
            CONFIG_KEY_AUTOSYNC: config[CONFIG_KEY_AUTOSYNC],
            CONFIG_KEY_SYNC_INT: config[CONFIG_KEY_SYNC_INT],
            CONFIG_KEY_MAXUSER: config[CONFIG_KEY_MAXUSER],
            CONFIG_KEY_FOCUS: config[CONFIG_KEY_FOCUS],
            CONFIG_KEY_MEDAL: config[CONFIG_KEY_MEDAL]
        }
        config_content[name] = value
        ConfigWrapper.write_config(config_content)

    @staticmethod
    def get_config_by_name(name, config={}):
        if config == {}:
            config = ConfigWrapper.get_config()

        if name in config:
            return config[name]
        else:
            return None
