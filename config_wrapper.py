from datetime import datetime
import json
from platform import release
from aqt import mw
from aqt.qt import QDialog, qtmajor
from aqt.utils import showInfo, showWarning, askUser
from anki.utils import isMac, isWin, isLin
from .calculator import *
from .client_api import ClientAPI
from .schemas import *

if qtmajor > 5:
    from ui.pyqt6UI import config, forgot_password, register, change_password
    from PyQt6 import QtCore, QtWidgets
else:
    from ui.pyqt5UI import config, forgot_password, register, change_password
    from PyQt5 import QtCore, QtWidgets

from . import version
import os

CONFIG_KEY_STATE_LOGIN = "is_login"
CONFIG_KEY_AUTHTOKEN = "access_token"
CONFIG_KEY_HOMESCREEN = "homescreen"
CONFIG_KEY_LEAGUE_INDEX = "league_index"
CONFIG_KEY_USERNAME = "username"

if isMac or isLin:
    PATH_DELIMITER = "/"
else:
    PATH_DELIMITER = "\\"
CURR_DIR = os.path.dirname(__file__)
DATA_DIR = CURR_DIR + PATH_DELIMITER + "json"
LEAGUES_INFO_FILE = DATA_DIR + PATH_DELIMITER + "leagues.json"
USERS_INFO_FILE = DATA_DIR + PATH_DELIMITER + "users.json"
LEAGUE_NAME_SPLITER = " - ss " 


# NOTE: For testing only
min_study_constraint = 20
############ End testing data #############


class ConfigWrapper(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.dialog_ui = config.Ui_ConfigDialog()
        self._is_signin = ConfigWrapper.get_config()[CONFIG_KEY_STATE_LOGIN]
        self.dialog_ui.setupUi(self)
        self.setupUI()
        self.connect_signals_slots()

    def setupUI(self):
        self.setWindowTitle(
            'AnkiVN Leaderboard Configuration - v{}'.format(version.__version__))
        self.dialog_ui.le_user.setText(ConfigWrapper.get_config()[CONFIG_KEY_USERNAME])
        self._update_auth_btn()

        if os.path.exists(LEAGUES_INFO_FILE):
            self.display_league_info_from_cache()
            self.dialog_ui.cb_leaderboard_challenge.setCurrentIndex(ConfigWrapper.get_config()[CONFIG_KEY_LEAGUE_INDEX])


        self.dialog_ui.tb_members.setColumnWidth(0, 200)
        self.dialog_ui.tb_members.setColumnWidth(1, 120)
        self.dialog_ui.tb_members.setColumnWidth(2, 120)
        self.dialog_ui.tb_leaderboard.setColumnWidth(0, 100)
        self.dialog_ui.tb_leaderboard.setColumnWidth(1, 60)
        self.dialog_ui.tb_leaderboard.setColumnWidth(2, 25)
        self.dialog_ui.tb_leaderboard.setColumnWidth(3, 30)
        self.dialog_ui.tb_leaderboard.setColumnWidth(4, 50)
        self.dialog_ui.tb_leaderboard.setColumnWidth(5, 60)
        self.dialog_ui.tb_leaderboard.setColumnWidth(6, 60)
        self.dialog_ui.tb_leaderboard.setColumnWidth(7, 50)
        self.dialog_ui.tb_leaderboard.setColumnWidth(8, 120)
        # self.dialog_ui.tb_leaderboard.setSortingEnabled(True)


        self.dialog_ui.cb_show_home.setEnabled(False)
        self.dialog_ui.lbl_time.setEnabled(False)
        if qtmajor > 5:
            self.dialog_ui.tb_leaderboard.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
            self.dialog_ui.tb_members.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        else:
            self.dialog_ui.tb_leaderboard.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
            self.dialog_ui.tb_members.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def connect_signals_slots(self):
        self.dialog_ui.btn_sync.released.connect(self._on_sync)
        self.dialog_ui.btn_cancel.released.connect(self._on_cancel)
        self.dialog_ui.btn_sign.released.connect(self._on_sign)
        self.dialog_ui.btn_register.released.connect(self._on_register)
        self.dialog_ui.btn_reset.released.connect(self._on_reset)
        self.dialog_ui.btn_refresh.released.connect(self._on_challenge_refresh)
        self.dialog_ui.btn_join.released.connect(self._on_challenge_join)
        self.dialog_ui.btn_refresh_user.released.connect(self._on_user_refresh)
        self.dialog_ui.cb_challenge.currentIndexChanged.connect(self.display_league_members_list_from_cache)
        self.dialog_ui.cb_leaderboard_challenge.currentIndexChanged.connect(self.display_league_data)
        self.dialog_ui.cb_user_manager.currentIndexChanged.connect(self.display_user_role)
        self.dialog_ui.btn_change_user_role.released.connect(self._on_set_user_role)

    def show_status(self, msg):
        self.dialog_ui.lbl_status.setText(msg)

    def focus_on_me(self):
        self.raise_()
        self.activateWindow()

    @staticmethod
    def showServerResponse(res):
        msg = f"ERROR: {res.status_code}!<br> Message: {res.text}"
        showWarning(msg)

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

        ConfigWrapper.write_config_by_name(CONFIG_KEY_STATE_LOGIN,self._is_signin)

    def display_users(self):
        if os.path.exists(USERS_INFO_FILE):
            with open(USERS_INFO_FILE, "r") as f:
                users = json.loads(f.read())
            self.dialog_ui.cb_user_manager.clear()
            for user in users:
                self.dialog_ui.cb_user_manager.addItem(user["username"])

    def display_user_role(self):
        if os.path.exists(USERS_INFO_FILE):
            with open(USERS_INFO_FILE, "r") as f:
                users = json.loads(f.read())
            current_user = self.dialog_ui.cb_user_manager.currentText()
            for user in users:
                if current_user == user["username"]:
                    self.dialog_ui.sp_user_role.setValue(user["role"])
                    return

    def _on_set_user_role(self):
        username = self.dialog_ui.cb_user_manager.currentText()
        role = self.dialog_ui.sp_user_role.value()
        access_token = self.get_config_by_name(CONFIG_KEY_AUTHTOKEN)
        res = ClientAPI.set_user_role(SetUserRoleRequest(username=username, role=role), access_token=access_token)
        if res is None:
            return
        if res.status_code != 202:
            ConfigWrapper.showServerResponse(res)
        else:
            self.dialog_ui.lbl_status.setText(f"Set role for user {username} successfully !")
                

    ### Slots ###
    def _on_user_refresh(self):
        res = ClientAPI.get_all_users()
        if res is None:
            return
        if res.status_code != 200:
            ConfigWrapper.showServerResponse(res)
            return
        
        with open(USERS_INFO_FILE, "w") as f:
            f.write(res.text)

        self.display_users()

    def _on_sign(self):
        user = self.dialog_ui.le_user.text()
        passwd = self.dialog_ui.le_password.text()
        if not self._is_signin:
            # Validate user and password
            if user == "" or passwd == "":
                msg = "Invalid user & password !"
                showWarning(msg)
                return
            else:
                res = ClientAPI.login(LoginRequest(username=user, password=passwd))
                if res is None:
                    return
                if res.status_code != 200:
                    ConfigWrapper.showServerResponse(res)
                    return
                authToken = json.loads(res.text)[CONFIG_KEY_AUTHTOKEN]
                ConfigWrapper.write_config_by_name(CONFIG_KEY_AUTHTOKEN, authToken)
                ConfigWrapper.write_config_by_name(CONFIG_KEY_USERNAME, user)
                self._is_signin = True
        else:
            self._is_signin = False
            ConfigWrapper.write_config_by_name(CONFIG_KEY_AUTHTOKEN, "")

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
            self.forgot_password_dialog_ui.buttonBox.rejected.connect(
                self._on_dialog_forgot_password_reject)
            self.forgot_password_dialog.show()

    def _on_sync(self):
        ConfigWrapper.write_config_by_name(CONFIG_KEY_LEAGUE_INDEX, self.dialog_ui.cb_leaderboard_challenge.currentIndex())
        name, season = self.get_league_name_season_from_cb_leaderboard_challenge()
        if name is None:
            showWarning("Challenge info on local is empty, refresh challenge in tab Challenge")
            return            
        league_info = ConfigWrapper.get_league_info_by_name(name, season)

        if league_info is None:
            showWarning("Challenge info on local is empty, refresh challenge in tab Challenge")
            return
        id = league_info["id"]
        start_timestamp=league_info["start_time"]
        duration=league_info["duration"]
        reset_point=league_info["reset"]
        study_days, _ = get_days_learned_season(start_timestamp=start_timestamp,
                                             duration=duration,
                                             reset_point=reset_point,
                                             constraint=min_study_constraint)
        #showInfo(study_days)
        reviews_today, retention_today = get_reviews_and_retention_today(reset_point=reset_point)
        reviews_league, retention_league = get_reviews_and_retention_season(start_timestamp=start_timestamp, duration=duration)
        sync_data = {
            "league_id": id,
            "streak": get_streak(reset_point=reset_point),
            "study_days": study_days,
            "reviews_today": reviews_today,
            "retention_today": retention_today,
            "minutes_today": get_time_spend_today(reset_point=reset_point),
            "reviews_league": reviews_league,
            "retention_league": retention_league,
            "minutes_league": get_time_spend_season(start_timestamp=start_timestamp, duration=duration)
        }
        access_token = self.get_config_by_name(CONFIG_KEY_AUTHTOKEN)
        res = ClientAPI.sync(req=SyncRequest(**sync_data), access_token=access_token)
        if res is None:
            return
        if res.status_code != 201 and res.status_code != 202:
            ConfigWrapper.showServerResponse(res)
            return
        else:
            now = get_datetime_now()
            self.show_status(f'Sync study data successfully at {now}')

        # get new league data
        res = ClientAPI.get_league_data(id=id)
        if res is None:
            return
        if res.status_code != 200:
            ConfigWrapper.showServerResponse(res)
            return

        filename = f"{DATA_DIR}{PATH_DELIMITER}{name}_{season}.json"
        with open(filename, "w") as f:
            f.write(res.text)
        self.display_league_data_from_cache(filename)

    def _on_cancel(self):
        self.close()

    def _on_register(self):
        self.register_dialog = QDialog()
        self.register_dialog_ui = register.Ui_Dialog()
        self.register_dialog_ui.setupUi(self.register_dialog)
        self.register_dialog_ui.buttonBox.accepted.connect(
            self._on_dialog_register_accept)
        self.register_dialog_ui.buttonBox.rejected.connect(
            self._on_dialog_register_reject)
        self.register_dialog.show()

    def _on_dialog_register_accept(self):
        username = self.register_dialog_ui.le_username.text()
        email = self.register_dialog_ui.le_email.text()
        password = self.register_dialog_ui.le_password.text()
        confirm = self.register_dialog_ui.le_confirm.text()
        if password != confirm:
            showWarning("Password is not matched ! Please check again.")
        else:
            res = ClientAPI.register(RegisterRequest(username=username, password=password, email=email))
            if res is None:
                return
            if res.status_code != 201:
                ConfigWrapper.showServerResponse(res)
            else:
                self.show_status(f"User {username} created successful!")
        self.register_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()
    def _on_dialog_register_reject(self):
        self.register_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    def _on_dialog_change_password_accept(self):
        old = self.change_password_dialog_ui.le_oldpass.text()
        new = self.change_password_dialog_ui.le_newpass.text()
        confirm = self.change_password_dialog_ui.le_confirmpass.text()

        if old == "" or new == "" or confirm == "":
            showWarning(f"Required field is empty !")
        else:
            if new != confirm:
                showWarning(f"Password is not matched ! Please check again.")
            else:
                # TODO: Handle reset password
                showWarning("This function is not supported")

        self.change_password_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    def _on_dialog_change_password_reject(self):
        self.change_password_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    def _on_dialog_forgot_password_accept(self):
        email = self.forgot_password_dialog_ui.le_email.text()
        # TODO: Handle forgot password
        showWarning("This function is not supported")

        showInfo("We'll send you a email to reset your password if your email was already in our system !<br>Please check spam folder also")
        self.forgot_password_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    def _on_dialog_forgot_password_reject(self):
        self.forgot_password_dialog_ui.buttonBox.disconnect()
        self.focus_on_me()

    def _on_challenge_refresh(self):
        res = ClientAPI.get_leagues()
        if res is None:
            return
        if res.status_code != 200:
            ConfigWrapper.showServerResponse(res)
        with open(LEAGUES_INFO_FILE, "w") as f:
            f.write(res.text)
        self.display_league_info_from_cache()
        self.display_league_members_list_from_cache()
        now = get_datetime_now()
        self.dialog_ui.lbl_status.setText(f"Updated challenge members at {now}")
    
    def _on_challenge_join(self):
        league_name, league_season = self.get_league_name_season_from_cb_challenge()
        access_token = self.get_config_by_name(CONFIG_KEY_AUTHTOKEN)
        req = LeagueBase(name=league_name, season=league_season)
        res = ClientAPI.join_league(req=req, access_token=access_token)
        if res is None:
            return
        if res.status_code != 202:
            ConfigWrapper.showServerResponse(res)
        # refresh status
        self._on_challenge_refresh()
    def _on_accept_join(self):
        buttonClicked = self.sender()
        index = self.dialog_ui.tb_members.indexAt(buttonClicked.pos())
        username = self.dialog_ui.tb_members.item(index.row(), 0).text()
        name, season = self.get_league_name_season_from_cb_challenge()
        req = AddUserRequest(username=username, league=LeagueBase(name=name, season=season))
        access_token = self.get_config_by_name(CONFIG_KEY_AUTHTOKEN)
        res = ClientAPI.add_member(req=req, access_token=access_token)
        if res is None:
            return
        if res.status_code != 202:
            ConfigWrapper.showServerResponse(res)
            return
        self.show_status(f"Added user {username} to {name} - ss {season} success !")

    def _on_get_users(self):
        pass

    @staticmethod
    def get_league_info_by_name(name: str, season: int):
        leagues_info = ConfigWrapper.get_leagues_info_from_cache()
        for league in leagues_info:
            if name == league["name"] and season == league["season"]:
                return league

        return None

    @staticmethod
    def get_leagues_info_from_cache():
        with open(LEAGUES_INFO_FILE, "r") as f:
            leagues_info = json.loads(f.read())
        return leagues_info

    def display_league_info_from_cache(self):
        self.dialog_ui.cb_challenge.clear()
        self.dialog_ui.cb_leaderboard_challenge.clear()
        self.dialog_ui.cb_delete_challenge.clear()
        leagues_info = ConfigWrapper.get_leagues_info_from_cache()
        
        for league in leagues_info:
            league_name = league["name"] + LEAGUE_NAME_SPLITER + str(league["season"])
            self.dialog_ui.cb_challenge.addItem(league_name)
            self.dialog_ui.cb_leaderboard_challenge.addItem(league_name)
            self.dialog_ui.cb_delete_challenge.addItem(league_name)
        
        #self.display_league_members_from_cache()

    def get_league_name_season_from_cb_leaderboard_challenge(self):
        tmp = self.dialog_ui.cb_leaderboard_challenge.currentText().split(LEAGUE_NAME_SPLITER)
        if len(tmp) != 2:
            return None, None
        league_name = tmp[0]
        league_season = int(tmp[1])
        return league_name, league_season

    def get_league_name_season_from_cb_challenge(self):
        tmp = self.dialog_ui.cb_challenge.currentText().split(LEAGUE_NAME_SPLITER)
        if len(tmp) != 2:
            return None, None
        league_name = tmp[0]
        league_season = int(tmp[1])
        return league_name, league_season

    def display_league_members_list_from_cache(self):
        league_name, league_season = self.get_league_name_season_from_cb_challenge()
        league = ConfigWrapper.get_league_info_by_name(league_name, league_season)

        if league is not None:
            users = league["users"]
            self.dialog_ui.tb_members.setRowCount(0)
            self.dialog_ui.tb_members.setRowCount(len(users))
            row = 0
            for user in users:
                self.dialog_ui.tb_members.setItem(row, 0, QtWidgets.QTableWidgetItem(user["username"]))
                if user["role"] == 0:
                    status = "submitted"
                    btn = QtWidgets.QPushButton(self.dialog_ui.tb_members)
                    btn.setText('Accept')
                    self.dialog_ui.tb_members.setCellWidget(row, 2, btn)
                    btn.released.connect(self._on_accept_join)
                else:
                    status = "joined"
                self.dialog_ui.tb_members.setItem(row, 1, QtWidgets.QTableWidgetItem(status))
                row += 1
    
    def display_league_data(self):
        name, season = self.get_league_name_season_from_cb_leaderboard_challenge()
        if name is None:
            return
        filename = f"{DATA_DIR}{PATH_DELIMITER}{name}_{season}.json"
        if os.path.exists(filename):
            self.display_league_data_from_cache(filename)
    
    def display_league_data_from_cache(self, filename: str):
        with open(filename, "r") as f:
            leagues_data = json.loads(f.read())
        users = leagues_data["users"]
        self.dialog_ui.tb_leaderboard.setRowCount(0)
        self.dialog_ui.tb_leaderboard.setRowCount(len(users))
        row = 0
        for user in users:
            day_off = user["day_over"] - user["study_days"]
            last_update = datetime.fromtimestamp(user["timestamp"])
            self.dialog_ui.tb_leaderboard.setItem(row, 0, QtWidgets.QTableWidgetItem(user["username"]))
            self.dialog_ui.tb_leaderboard.setItem(row, 1, QtWidgets.QTableWidgetItem(str(user["xp"])))
            self.dialog_ui.tb_leaderboard.setItem(row, 2, QtWidgets.QTableWidgetItem(str(user["day_over"])))
            self.dialog_ui.tb_leaderboard.setItem(row, 3, QtWidgets.QTableWidgetItem(str(user["streak"])))
            self.dialog_ui.tb_leaderboard.setItem(row, 4, QtWidgets.QTableWidgetItem(str(day_off)))
            self.dialog_ui.tb_leaderboard.setItem(row, 5, QtWidgets.QTableWidgetItem(str(user["reviews"])))
            self.dialog_ui.tb_leaderboard.setItem(row, 6, QtWidgets.QTableWidgetItem(str(user["retention"])))
            self.dialog_ui.tb_leaderboard.setItem(row, 7, QtWidgets.QTableWidgetItem(str(user["minutes"])))
            self.dialog_ui.tb_leaderboard.setItem(row, 8, QtWidgets.QTableWidgetItem(str(last_update)))
            row+=1

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
            CONFIG_KEY_AUTHTOKEN: config[CONFIG_KEY_AUTHTOKEN],
            CONFIG_KEY_HOMESCREEN: config[CONFIG_KEY_HOMESCREEN],
            CONFIG_KEY_STATE_LOGIN: config[CONFIG_KEY_STATE_LOGIN],
            CONFIG_KEY_LEAGUE_INDEX: config[CONFIG_KEY_LEAGUE_INDEX],
            CONFIG_KEY_USERNAME: config[CONFIG_KEY_USERNAME]
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
