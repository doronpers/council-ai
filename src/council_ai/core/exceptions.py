"""
Custom exceptions for Council AI.

Provides a hierarchy of exceptions for better error handling and user messaging.
"""


class CouncilError(Exception):
    """Base exception for all Council AI errors."""

    pass


class ConfigurationError(CouncilError):
    """Error in configuration or setup."""

    pass


class APIError(CouncilError):
    """Base class for API-related errors."""

    pass


class APIKeyError(APIError):
    """Invalid or missing API key."""

    def __init__(self, provider: str, message: str = ""):
        self.provider = provider
        default_msg = f"Invalid or missing API key for provider '{provider}'"
        super().__init__(message or default_msg)


class RateLimitError(APIError):
    """API rate limit exceeded."""

    def __init__(self, provider: str, retry_after: int = None, message: str = ""):
        self.provider = provider
        self.retry_after = retry_after
        default_msg = f"Rate limit exceeded for provider '{provider}'"
        if retry_after:
            default_msg += f". Retry after {retry_after} seconds"
        super().__init__(message or default_msg)


class TimeoutError(CouncilError):
    """Operation timed out."""

    def __init__(self, operation: str, timeout: float, message: str = ""):
        self.operation = operation
        self.timeout = timeout
        default_msg = f"Operation '{operation}' timed out after {timeout}s"
        super().__init__(message or default_msg)


class TransientAPIError(APIError):
    """Transient API error that may succeed on retry."""

    def __init__(self, provider: str, original_error: Exception, message: str = ""):
        self.provider = provider
        self.original_error = original_error
        default_msg = f"Transient error from provider '{provider}': {str(original_error)}"
        super().__init__(message or default_msg)


class PersonaNotFoundError(CouncilError):
    """Requested persona does not exist."""

    def __init__(self, persona_id: str, message: str = ""):
        self.persona_id = persona_id
        default_msg = f"Persona '{persona_id}' not found"
        super().__init__(message or default_msg)


class DomainNotFoundError(CouncilError):
    """Requested domain does not exist."""

    def __init__(self, domain_id: str, message: str = ""):
        self.domain_id = domain_id
        default_msg = f"Domain '{domain_id}' not found"
        super().__init__(message or default_msg)


class ConsultationError(CouncilError):
    """Error during consultation process."""

    def __init__(self, message: str, partial_responses: list = None):
        self.partial_responses = partial_responses or []
        super().__init__(message)


class ProviderUnavailableError(APIError):
    """No available providers for the request."""

    def __init__(self, attempted_providers: list = None, message: str = ""):
        self.attempted_providers = attempted_providers or []
        default_msg = "No available providers"
        if attempted_providers:
            default_msg += f". Tried: {', '.join(attempted_providers)}"
        super().__init__(message or default_msg)
