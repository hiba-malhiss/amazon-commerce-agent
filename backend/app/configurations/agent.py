"""Agent-level configuration.

The objective text lives here, not in the prompts, so the prompts stay general and the
domain specifics (what this store does, which policies it covers) are configuration.
"""

AGENT_OBJECTIVE = (
    "You help shoppers of an online store: search for products, and answer questions about "
    "the store's policies (returns, shipping, warranty, payment)."
)
