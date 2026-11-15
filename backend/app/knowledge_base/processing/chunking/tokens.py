import tiktoken

# The tokenizer of OpenAI's current chat and embedding models
encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(encoding.encode(text))
