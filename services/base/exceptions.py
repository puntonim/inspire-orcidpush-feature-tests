

class BaseException(Exception):
    http_status_code = 500
    raw_response = None

    @classmethod
    def match(cls, response):
        return response.status_code == cls.status_code
