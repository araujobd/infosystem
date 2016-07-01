
class InfoSystemException(Exception):

    status = 500
    message = ''


class NotFound(InfoSystemException):

    status = 404
    message = 'Entity not found'


class BadRequest(InfoSystemException):

    status = 400
    message = 'Provided body does not represent a valid entity'


class BadRequestContentType(BadRequest):

    message = 'Content-Type header must be application/json'
