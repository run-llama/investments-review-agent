class LlamaCloudAPIError(Exception):
    """Base exception for all LlamaCloud API-related errors."""

    pass


class ClassificationError(LlamaCloudAPIError):
    """Exception raised when document classification fails or returns invalid data."""

    pass


class ExtractionError(LlamaCloudAPIError):
    """Exception raised when data extraction fails or returns invalid data."""

    pass


class SheetParsingError(LlamaCloudAPIError):
    """Exception raised when sheet parsing fails or returns invalid data."""

    pass
