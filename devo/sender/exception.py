class DevoSenderException(Exception):
    """ Default Devo Sender Exception for functionalities related to sending
     events to the platform"""

    def __init__(self, message: str):
        """
        Creates an exception related to event sending tasks

        :param message: Message describing the exception. It will be also
         used as `args` attribute in `Exception` class
        """
        self.message: str = message
        """Message describing exception"""
        super().__init__(self.message)
