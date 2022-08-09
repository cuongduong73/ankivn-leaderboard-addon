import re


def validate_username(username: str) -> bool:
    # username is 6-20 characters long
    # no _ or . at the beginning
    # no __ or _. or ._ or .. inside
    # allowed characters a-z, A-Z, 0-9, _
    # no _ or . at the end
    pattern = re.compile("^(?=[a-zA-Z0-9_]{6,20}$)(?!.*[_.]{2})[^_.].*[^_.]$")
    return False if pattern.match(username) is None else True


def validate_password(password: str) -> bool:
    # [8-20] characters, at least one letter and one number
    pattern = re.compile("^(?=.*[A-Za-z])(?=.*\d)[\w~@#$%^&*+=`|{}:;!.?\"()\[\]-]{8,20}$")
    return False if pattern.match(password) is None else True
