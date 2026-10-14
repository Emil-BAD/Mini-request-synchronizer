class OrdersSourceError(RuntimeError):
    def __init__(self, message: str, status_code: int = 503, detail: str | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
