"""Replay 'compare it to the third option' with the updated prompt: both the 'it' request
and the 'third option' request should resolve (pass check_references), so both cards show."""

import ast
import asyncio
import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.prompts.understanding import UNDERSTANDING_PROMPT
from app.agent.schemas.understanding import understanding_schema
from app.agent.utils.references import check_references
from app.configurations.parameters import PARAMETERS
from app.configurations.tools.registry import TOOLS

PROMPT = open("/tmp/u3.txt").read()
VISIBLE = ast.literal_eval(re.search(r"\[\[\{'reference'.*\]\]", PROMPT, re.S).group(0))
MESSAGE = "compare it to the third option"


async def main():
    references = [c["reference"] for lst in VISIBLE for c in lst]
    label_by_reference = {c["reference"]: c["product_name"] for lst in VISIBLE for c in lst}

    system = SystemMessage(
        content=UNDERSTANDING_PROMPT.format(
            parameters=[p.model_dump() for p in PARAMETERS],
            tools=[{"code": t.code, "name": t.name, "description": t.description,
                    "required_parameters": t.required_parameters,
                    "optional_parameters": t.optional_parameters} for t in TOOLS],
            recent_requests=[],
            visible_results=VISIBLE,
        )
    )
    # The in-focus product (INSIGNIA 43", card 1 of the newest list) was just detailed.
    history = [
        HumanMessage(content="more options"),
        AIMessage(content="Here are more TV options..."),
        HumanMessage(content="tell me about the INSIGNIA 43"),
        AIMessage(content="The INSIGNIA 43\" Class F50 ... 4.3 stars."),
        HumanMessage(content=MESSAGE),
    ]

    for trial in range(3):
        out = await (__import__("app.llm.client", fromlist=["llm_client"]).llm_client
                     .structured_completion(messages=[system, *history],
                                            response_schema=understanding_schema(references)))
        ok = True
        rows = []
        for req in out.requests:
            clar = check_references(req.model_dump(), label_by_reference, MESSAGE)
            rows.append((req.reference_quote, req.referenced_entities, clar))
            if clar is not None:
                ok = False
        print(f"trial {trial + 1}: all_resolve={ok}")
        for quote, refs, clar in rows:
            print(f"    quote={quote!r:18} refs={refs} clarify={clar!r}")


asyncio.run(main())
