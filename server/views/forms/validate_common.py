import string


def valid_password_rules(password):
    if len(password) < 8:
        return False

    if not (any(x.isupper() for x in password) and any(x.islower() for x in password)):
        return False

    if not any(x.isdigit() for x in password):
        return False

    if len(set(string.punctuation).intersection(password)) == 0:
        return False

    return True
