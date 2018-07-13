

class BaseJsonResponse(dict):
    exceptions = []

    def __init__(self, response):
        self.raw_response = response
        try:
            data = response.json()
        except ValueError:
            data = response.content
        super(BaseJsonResponse, self).__init__(data)

    @property
    def ok(self):
        return self.raw_response.ok

    @property
    def status_code(self):
        return self.raw_response.status_code

    def raise_for_result(self):
        """
        Raise one of the known exceptions (in self.exceptions) depending on the
        matching criteria; or raise requests.exceptions.HTTPError.
        In case of no errors no exception is raised.
        """
        for exception_class in self.exceptions:
            if exception_class.match(self):
                message = ''
                exception_object = exception_class(message)
                exception_object.raw_response = self.raw_response
                raise exception_object
        # Can raise requests.exceptions.HTTPError.
        return self.raw_response.raise_for_status()
