import requests
from .schemas import *
from aqt.utils import showWarning

API_ROOT_URL = "https://ankivn.herokuapp.com"

USER_ROUTE = "/user"
LOGIN_ROUTE = "/login"

LEAGUE_ROUTE = "/league"
ADD_USER_ROUTE = LEAGUE_ROUTE + "/add_user"
LEAGUE_JOIN_ROUTE = LEAGUE_ROUTE + "/join"
LEAGUE_SYNC_ROUTE = LEAGUE_ROUTE + "/sync"
LEAGUE_DATA_ROUTE = LEAGUE_ROUTE + "/data"

class ClientAPI:
    @staticmethod
    def login(req: LoginRequest):
        try:
            res = requests.post(API_ROOT_URL+LOGIN_ROUTE, data=req.dict())
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}")
        

    @staticmethod
    def get_leagues():
        try:
            res = requests.get(API_ROOT_URL+LEAGUE_ROUTE)
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}")

    @staticmethod
    def join_league(req: LeagueBase, access_token: str):
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            res = requests.post(API_ROOT_URL+LEAGUE_JOIN_ROUTE, data=req.json(), headers=headers)
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}")

    @staticmethod
    def register(req: RegisterRequest):
        try:
            res = requests.post(API_ROOT_URL+USER_ROUTE, data=req.json())
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}")

    @staticmethod
    def add_member(req: AddUserRequest, access_token: str):
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            res = requests.post(API_ROOT_URL+ADD_USER_ROUTE, data=req.json(), headers=headers)
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}")

    @staticmethod
    def sync(req: SyncRequest, access_token: str):
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            res = requests.post(API_ROOT_URL+LEAGUE_SYNC_ROUTE, data=req.json(), headers=headers)
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}")       
    
    @staticmethod
    def get_league_data(id: int):
        try:
            res = requests.get(API_ROOT_URL+LEAGUE_DATA_ROUTE+"/"+str(id))
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}")

    @staticmethod
    def get_all_users():
        try:
            res = requests.get(API_ROOT_URL+USER_ROUTE)
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}") 

    @staticmethod
    def set_user_role(req: SetUserRoleRequest, access_token: str):
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            res = requests.put(API_ROOT_URL+USER_ROUTE, data=req.json(), headers=headers)
            return res
        except requests.exceptions.HTTPError as errh:
            showWarning (f"Http Error:{errh}")
        except requests.exceptions.ConnectionError as errc:
            showWarning (f"Error Connecting:{errc}")
        except requests.exceptions.Timeout as errt:
            showWarning (f"Timeout Error:{errt}")
        except requests.exceptions.RequestException as err:
            showWarning (f"OOps: Something Else{err}")                


