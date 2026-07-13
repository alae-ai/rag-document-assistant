"""
Configuration for prompt generation.
"""

# Name of the prompt template located in the prompts/ directory.
PROMPT_TEMPLATE = "system_prompt.txt"

# Maximum number of characters allowed in the retrieved context.
MAX_CONTEXT_LENGTH = 4000

# Include the source metadata (filename) before each retrieved chunk.
INCLUDE_SOURCES = True

# Add separators between retrieved chunks.
USE_CHUNK_SEPARATORS = True

# Separator used between chunks.
CHUNK_SEPARATOR = "\n\n--------------------\n\n"
