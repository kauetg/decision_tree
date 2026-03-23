"""
key.py
------
Generates a dichotomous identification key from a character state matrix.

Logic: autapomorphy-based splitting
    At each node, find a character with a state exclusive to a subgroup.
    That character becomes the diagnostic question.
    If no diagnostic character exists → taxa are indistinguishable
    with the current matrix → user must add more characters.

Key JSON structure (consumed by front-end):
    {
        "type": "question",
        "character": "colony_shape",
        "state": "branching",
        "yes": { ... },   # subgroup that HAS this state
        "no":  { ... }    # subgroup that DOES NOT have this state
    }

    or, at a leaf:
    {
        "type": "result",
        "taxon": "Acropora palmata"
    }

    or, when taxa are indistinguishable:
    {
        "type": "warning",
        "taxa": ["Acropora palmata", "Acropora cervicornis"],
        "message": "Cannot distinguish these taxa with current characters.
                    Add more characters to your matrix."
    }
"""


# --- PUBLIC ---

def build_key(payload: dict) -> dict:
    """
    Build a dichotomous identification key from the front-end payload.

    Args:
        payload: dict with keys 'characters', 'taxa', 'matrix'

    Returns:
        dict: nested key JSON ready for front-end rendering
    """
    characters  = [c['name'] for c in payload['characters']]
    taxa        = [t['name'] for t in payload['taxa'] if not t['outgroup']]
    matrix      = payload['matrix']

    # outgroup is excluded from the key —
    # it's the reference point, not an identification target
    return _build_node(taxa, characters, matrix)


# --- PRIVATE ---

def _build_node(taxa: list[str], characters: list[str], matrix: dict) -> dict:
    """
    Recursively build a key node for a group of taxa.

    Args:
        taxa       : list of taxon names in this group
        characters : list of character names available
        matrix     : full state matrix {taxon: {character: state}}

    Returns:
        dict: key node (question, result, or warning)
    """

    # --- BASE CASE: single taxon identified ---
    if len(taxa) == 1:
        return {
            "type": "result",
            "taxon": taxa[0]
        }

    # --- find best diagnostic character ---
    question = _find_diagnostic_character(taxa, characters, matrix)

    # --- no diagnostic character found ---
    if question is None:
        return {
            "type": "warning",
            "taxa": taxa,
            "message": (
                f"Cannot distinguish {' vs '.join(taxa)} "
                f"with current characters. "
                f"Add more characters to your matrix."
            )
        }

    character, state, yes_group, no_group = question

    return {
        "type": "question",
        "character": character,
        "state": state,
        "yes": _build_node(yes_group, characters, matrix),
        "no":  _build_node(no_group,  characters, matrix)
    }


def _find_diagnostic_character(
    taxa: list[str],
    characters: list[str],
    matrix: dict
) -> tuple | None:
    """
    Find a character with a state exclusive to at least one subgroup.

    Strategy:
        For each character, collect all states present in this group.
        If any state is shared by a strict subset of taxa (not all, not one):
            → that state is diagnostic for that subset
            → return (character, state, yes_group, no_group)

        Priority: prefer splits that isolate the smallest subgroup first
        (more specific questions come before broader ones).

    Returns:
        (character, state, yes_group, no_group) if found
        None if no diagnostic character exists
    """
    best = None
    best_yes_size = len(taxa)  # prefer smaller yes_group

    for character in characters:

        # collect state → [taxa that have this state]
        state_map: dict[str, list[str]] = {}

        for taxon in taxa:
            state = matrix.get(taxon, {}).get(character, '')
            if not state:
                continue
            state_map.setdefault(state, []).append(taxon)

        # look for a state that isolates a strict subset
        for state, group in state_map.items():
            yes_group = group
            no_group  = [t for t in taxa if t not in yes_group]

            # skip if state applies to ALL taxa (not diagnostic)
            if len(yes_group) == len(taxa):
                continue

            # skip if state applies to NONE (missing data edge case)
            if len(yes_group) == 0:
                continue

            # valid split found — prefer the one with smallest yes_group
            if len(yes_group) < best_yes_size:
                best = (character, state, yes_group, no_group)
                best_yes_size = len(yes_group)

    return best