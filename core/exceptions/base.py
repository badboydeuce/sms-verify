class DeuceVerifyException(Exception):

    default_message = "Something went wrong"

    def __init__(
        self,
        message=None
    ):

        self.message = (
            message or self.default_message
        )

        super().__init__(self.message)