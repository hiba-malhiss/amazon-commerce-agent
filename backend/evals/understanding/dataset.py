"""One-turn Understanding cases: a single user message with no earlier conversation.

Each case says what Understanding should return:
- requests: one entry per expected request, in order, with the tool and the parameters
  that must be there. A string parameter matches if the output contains it (case
  insensitive), so "headphones" matches "wireless headphones"; numbers must be equal.
- out_of_scope: whether the message asks for something no tool can do.
"""

DATASET_NAME = "understanding-one-turn"

EXAMPLES = [
    {
        "inputs": {"message": "find wireless headphones under $100"},
        "outputs": {
            "requests": [
                {
                    "tool": "search_products",
                    "parameters": {"product_name": "headphones", "max_price": 100},
                }
            ],
            "out_of_scope": False,
        },
        "metadata": {"category": "single_search"},
    },
    {
        "inputs": {"message": "show me samsung tvs between $300 and $500"},
        "outputs": {
            "requests": [
                {
                    "tool": "search_products",
                    "parameters": {"product_name": "tv", "min_price": 300, "max_price": 500},
                }
            ],
            "out_of_scope": False,
        },
        "metadata": {"category": "single_search"},
    },
    {
        "inputs": {"message": "cheap gaming keyboards under 50 dollars"},
        "outputs": {
            "requests": [
                {
                    "tool": "search_products",
                    "parameters": {"product_name": "keyboard", "max_price": 50},
                }
            ],
            "out_of_scope": False,
        },
        "metadata": {"category": "single_search"},
    },
    {
        "inputs": {"message": "find a laptop and a wireless mouse under $30"},
        "outputs": {
            "requests": [
                {"tool": "search_products", "parameters": {"product_name": "laptop"}},
                {
                    "tool": "search_products",
                    "parameters": {"product_name": "mouse", "max_price": 30},
                },
            ],
            "out_of_scope": False,
        },
        "metadata": {"category": "multiple_requests"},
    },
    {
        "inputs": {"message": "بدي سماعات بلوتوث بأقل من 50 دولار"},
        "outputs": {
            "requests": [{"tool": "search_products", "parameters": {"max_price": 50}}],
            "out_of_scope": False,
        },
        "metadata": {"category": "arabic"},
    },
    {
        "inputs": {"message": "what's your return policy?"},
        "outputs": {"requests": [], "out_of_scope": True},
        "metadata": {"category": "out_of_scope"},
    },
    {
        "inputs": {"message": "book me a flight to Paris next week"},
        "outputs": {"requests": [], "out_of_scope": True},
        "metadata": {"category": "out_of_scope"},
    },
    {
        "inputs": {"message": "hi there!"},
        "outputs": {"requests": [], "out_of_scope": False},
        "metadata": {"category": "greeting"},
    },
]
