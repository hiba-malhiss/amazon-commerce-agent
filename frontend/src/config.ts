// Mirrors backend/app/core/settings.py → max_user_message_length
export const MAX_MESSAGE_LENGTH = 4000;

// Threads loaded per page in the sidebar (more load on scroll)
export const THREADS_PAGE_SIZE = 20;

// Knowledge base uploads. Mirrors backend: converter.py → SUPPORTED_SUFFIXES,
// settings.py → max_upload_mb
export const KNOWLEDGE_FILE_TYPES = [".pdf", ".txt", ".md"];
export const MAX_UPLOAD_MB = 20;
