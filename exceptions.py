
class ExeptionBase(Exception):
    code = None
    message = ''

    def __init__(self, message='', code=''):
        self.message = '{}: {}'.format(self.message, message)
        if code:
            self.code = code


class MissingAttribute(ExeptionBase):
    code = ''
    message = ''


class NonValidAttribute(ExeptionBase):
    code = None
    message = ''


class InvalidTimeFormat(ExeptionBase):
    code = None
    message = ''


class EmployeeDoesNotExist(ExeptionBase):
    code = None
    message = ''