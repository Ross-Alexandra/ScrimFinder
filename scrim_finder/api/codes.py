from enum import Enum

# User Error Codes
UserCodes = Enum(
    "UserCodes",
    (
        "BadContact",
        "MissingParameters",
        "DoubleBooking",
        "PendingProposal"
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
        "ExceptionError",
        "ScrimCreated",
        "ProposalCreated"
    ),
    start=1000
)