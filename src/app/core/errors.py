class NotFoundError(Exception):
    message = 'Not Found'


class InternalServerError(Exception):
    message = 'Internal server error'


class ForbiddenError(Exception):
    message = 'Access denied'


class UnauthorizedError(Exception):
    message = 'You must be authorized'


class LoginError(Exception):
    message = 'Email or password is incorrect'


class RegisterError(Exception):
    message = 'User with this email already exists'
