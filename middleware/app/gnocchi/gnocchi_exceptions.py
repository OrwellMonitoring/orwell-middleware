from http import HTTPStatus

class CouldNotLoginGnocchi(Exception):
    def __init__(self, id=None, secret=None):
        self.status_code = HTTPStatus.UNAUTHORIZED
        if id and secret:
            self.message = f'Could not login on OpenStack"'
        else:
            self.message = 'Could not get authentication token from OpenStack'
        super().__init__(self.message)

    def __str__(self):
        return self.message