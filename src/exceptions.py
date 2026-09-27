class SecurityChallengeError(Exception):
    """Raised when the target website presents a security challenge."""


class SearchResultsNotFoundError(Exception):
    """Raised when search results cannot be found."""


class CompanyDataNotFoundError(Exception):
    """Raised when company data cannot be extracted."""