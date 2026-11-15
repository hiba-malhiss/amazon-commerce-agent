class KnowledgeBaseError(Exception):
    """An error the API returns to the caller, with its HTTP status."""

    status_code = 400


class NotFoundError(KnowledgeBaseError):
    status_code = 404


class FileTooLargeError(KnowledgeBaseError):
    status_code = 413
