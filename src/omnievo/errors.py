class OmniEvoError(Exception):
    """Base error for protocol or tool failures."""


class ProtocolError(OmniEvoError):
    """A request would violate the frozen scientific protocol."""


class BudgetError(ProtocolError):
    """A request would exceed a round or run assay budget."""


class OracleIntegrityError(OmniEvoError):
    """The private oracle is malformed or ambiguous."""


class LabClientError(OmniEvoError):
    """The virtual-lab service rejected or failed a request."""

