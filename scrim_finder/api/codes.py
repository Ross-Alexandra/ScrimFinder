from enum import Enum

# User Error Codes
UserCodes = Enum(
    "UserCodes",
    (
        "BadContact",
        "MissingParameters"
    ),
    start=0
)

# System Error Codes
SystemCodes = Enum(
    ""
    "SystemCodes",
    (
        "Good",
        "CommunicationError",
        "ExceptionError"
    ),
    start=1000
)