"""Reference cases: the user points at results they were shown ("the third one", "the PNY
one"), after a search and a reply. Taken from a real conversation where "the third one"
was resolved to the third product the reply MENTIONED instead of card 3.

Each case expects the product ids the agent ends up fetching, or a clarification.
"""

DATASET_NAME = "references"

# The 10 cards the user saw, in order (thread ef533c9e-…)
SSD_CARDS = [
    {
        "product_id": "B0H1NH99GX",
        "product_name": "Samsung Internal SSD 990 1TB, Read/Write Speeds Up to 7,150/6,450 MB/s",
        "price": 189.99,
    },
    {
        "product_id": "B0FGPXJMK1",
        "product_name": "SIX 1TB SATA 2.5 SSD Internal Solid State Hard Drive Read up to 560MB/s",
        "price": 125.99,
    },
    {
        "product_id": "B0DBR3DZWG",
        "product_name": "Kingston NV3 1TB M.2 2280 NVMe SSD | PCIe 4.0 Gen 4x4 | Up to 6000 MB/s",
        "price": 159.99,
    },
    {
        "product_id": "B0H4H1SNMY",
        "product_name": "SANDISK 1TB Portable SSD, Up to 1000MB/s Read Speeds, Black (New Model)",
        "price": 159.99,
    },
    {
        "product_id": "B07Y5VDNT9",
        "product_name": 'PNY CS900 1TB 2.5" SATA III Internal SSD',
        "price": 129.99,
    },
    {
        "product_id": "B0BF5JHWVR",
        "product_name": (
            "1TB SSD NVMe M.2 2280 PCIe Gen3x4 Internal Solid State Drive, Read Up to 2500MB/s"
        ),
        "price": 135.99,
    },
    {
        "product_id": "B0BHJF2VRN",
        "product_name": "Samsung SSD 990 PRO 1TB, PCIe 4.0 M.2 2280, Up to 7,450 MB/s",
        "price": 259.99,
    },
    {
        "product_id": "B0G42FGS7V",
        "product_name": (
            'Silicon Power 1TB SSD 3D NAND A55 SLC Cache Performance Boost SATA III 2.5"'
        ),
        "price": 127.97,
    },
    {
        "product_id": "B0H3XD9351",
        "product_name": "Sandisk 1TB Portable Drive, Up to 600MB/s Read Speeds - Black",
        "price": 129.99,
    },
    {
        "product_id": "B08GJCS69D",
        "product_name": "Timetec 1TB SSD 3D NAND SATA III 6Gb/s 2.5 Inch Read Speed Up to 550 MB/s",
        "price": 118.99,
    },
]

# The real first turn: its reply names products in an order unlike the cards'
SSD_HISTORY = [
    ["human", "Cheapest 1TB SSD from a known brand"],
    [
        "ai",
        "The cheapest 1TB SSD from a known brand in the results is the Timetec 1TB SSD "
        "SATA III 2.5 Inch priced at $118.99. It offers read speeds up to 550 MB/s. This "
        "is followed closely by the Silicon Power 1TB SATA III SSD at $127.97 and the PNY "
        "CS900 1TB SATA III SSD at $129.99.",
    ],
]


def case(case_id: str, message: str, expected: dict, category: str) -> dict:
    return {
        "inputs": {"history": SSD_HISTORY, "cards": SSD_CARDS, "message": message},
        "outputs": expected,
        "metadata": {"id": case_id, "category": category},
    }


EXAMPLES = [
    case(
        "third_one_after_ranked_reply",
        "give me more details regarding the third one?",
        {"product_ids": ["B0DBR3DZWG"]},
        "position",
    ),
    case("last_one", "and the last one?", {"product_ids": ["B08GJCS69D"]}, "position"),
    case(
        "first_and_fifth",
        "compare the first and the fifth one",
        {"product_ids": ["B0H1NH99GX", "B07Y5VDNT9"]},
        "position",
    ),
    case("out_of_range", "tell me about the 12th one", {"clarification": True}, "position"),
    case("by_brand", "tell me more about the PNY one", {"product_ids": ["B07Y5VDNT9"]}, "name"),
    case(
        "by_price",
        "details of the cheapest one please",
        {"product_ids": ["B08GJCS69D"]},
        "description",
    ),
    case("ambiguous_brand", "is the samsung one any good?", {"clarification": True}, "ambiguous"),
]
