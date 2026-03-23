"""
matrix.py
---------
Builds a pairwise distance matrix from a character state payload.

Distance metric: simple mismatch proportion
    distance(a, b) = characters_different / total_characters_compared

This is a PHENETIC approach — groups by field-observable similarity,
not by evolutionary history. See WARNING in result.html.

Input payload structure (from front-end JSON):
{
    "characters": [{"name": "shape", "states": ["branching", "massive"]}],
    "taxa":       [{"name": "Acropora", "outgroup": false}, ...],
    "matrix":     {"Acropora": {"shape": "branching"}, ...}
}
"""

import numpy as np


# --- PUBLIC ---

def build_distance_matrix(payload: dict) -> tuple[np.ndarray, list[str]]:
    """
    Build a symmetric pairwise distance matrix from the front-end payload.

    Returns:
        dist_matrix : np.ndarray, shape (n_taxa, n_taxa)
        taxon_names : list[str], ordered — outgroup last
    """
    characters  = payload['characters']
    taxa        = payload['taxa']
    matrix      = payload['matrix']

    taxon_names = _get_ordered_taxa(taxa)
    char_names  = [c['name'] for c in characters]

    n = len(taxon_names)
    dist_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            d = _compare_pair(
                taxon_names[i],
                taxon_names[j],
                char_names,
                matrix
            )
            dist_matrix[i][j] = d
            dist_matrix[j][i] = d  # symmetric

    return dist_matrix, taxon_names


# --- PRIVATE ---

def _get_ordered_taxa(taxa: list[dict]) -> list[str]:
    """
    Return taxon names with outgroup placed last.
    Outgroup last = scipy linkage roots the tree correctly.
    """
    ingroup  = [t['name'] for t in taxa if not t['outgroup']]
    outgroup = [t['name'] for t in taxa if t['outgroup']]
    return ingroup + outgroup


def _compare_pair(
    taxon_a: str,
    taxon_b: str,
    char_names: list[str],
    matrix: dict
) -> float:
    """
    Compute distance between two taxa as mismatch proportion.

    - Missing states ('', None) are skipped (not penalised).
    - If no characters can be compared, returns 0.0.

    Example:
        Acropora: shape=branching, symbiont=zooxanthellate
        Porites:  shape=massive,   symbiont=zooxanthellate
        → 1 mismatch / 2 compared = 0.5
    """
    mismatches = 0
    compared   = 0

    states_a = matrix.get(taxon_a, {})
    states_b = matrix.get(taxon_b, {})

    for char in char_names:
        state_a = states_a.get(char, '')
        state_b = states_b.get(char, '')

        # skip if either taxon has no state for this character
        if not state_a or not state_b:
            continue

        compared += 1
        if state_a != state_b:
            mismatches += 1

    if compared == 0:
        return 0.0

    return mismatches / compared