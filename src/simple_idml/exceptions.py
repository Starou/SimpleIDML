class InDesignSoapException(BaseException):
    _error = None

    def __init__(self, script_params, response):
        self._error = "Script params: %s\nResponse:  %s" % (script_params, response)

    def __str__(self):
        return repr(self._error)
