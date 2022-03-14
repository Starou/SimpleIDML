class InDesignSoapException(BaseException):
    _error = None

    def __init__(self, script_params, response):
        self._error = f"Script params: {script_params}\nResponse: {response}"

    def __str__(self):
        return repr(self._error)
