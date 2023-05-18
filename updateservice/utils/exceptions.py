class InvalidIdError(Exception):
    def __init__(self, message):
        self.message = message


class InvalidUserIdError(InvalidIdError):
    def __init__(self):
        message = "The user with the id requested does not exist"
        InvalidIdError.__init__(self, message)


class InvalidAppIdError(InvalidIdError):
    def __init__(self):
        message = "The application with the id requested does not exist"
        InvalidIdError.__init__(self, message)


class InvalidTeamIdError(InvalidIdError):
    def __init__(self):
        message = "The team with the id requested does not exist"
        InvalidIdError.__init__(self, message)


class InvalidPackageIdError(InvalidIdError):
    def __init__(self):
        message = "The package with the id requested does not exist"
        InvalidIdError.__init__(self, message)


class InvalidGroupIdError(InvalidIdError):
    def __init__(self):
        message = "The group with the id requested does not exist"
        InvalidIdError.__init__(self, message)


class TokenNotFound(Exception):
    def __init__(self):
        self.message = f"Could not find this token in data base"


class UserTokenNotFound(Exception):
    def __init__(self):
        self.message = f"Could not find this token for the requested user"


class TokenDeletedError(Exception):
    def __init__(self):
        self.message = f"The token you have used was deleted"


class TeamIdError(Exception):
    def __init__(self, team_id):
        self.message = {
            "error": {"message": f"Team {team_id} does not exist", "code": 404}
        }


class UsersNotFoundError(Exception):
    def __init__(self, search):
        self.message = f"No users found for '{search}'"


class ApplicationNotFoundError(Exception):
    def __init__(self, search):
        self.message = f"No applications found for '{search}'"


class AlreadyAssignedError(Exception):
    def __init__(self, application_id, group_id):
        self.message = (
            f"Application {application_id} already assign to group {group_id}"
        )


class NotAssignedError(Exception):
    def __init__(self, application_id, group_id):
        self.message = f"Application {application_id} not assigned to group {group_id}"


class ApplicationAssignedError(Exception):
    def __init__(self):
        self.message = f"Can not delete groups with apllications assigned to it"
