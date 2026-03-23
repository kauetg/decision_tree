"""
tree.py
-------
Builds a phenogram from a pairwise distance matrix using UPGMA,
then converts the result to ECharts-compatible hierarchical JSON.

Pipeline:
    dist_matrix + taxon_names (from matrix.py)
        → scipy linkage (UPGMA)
        → recursive build_node()
        → {"name": "root", "children": [...]}
        → ECharts renders it beautifully 🌳

Remember: this is a PHENOGRAM, not a phylogeny.
Groups reflect field-observable similarity, not evolutionary history.
"""

import numpy as np
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform


# --- PUBLIC ---

def build_tree(dist_matrix: np.ndarray, taxon_names: list[str], matrix: dict = {}) -> dict:
    """
    Run UPGMA on the distance matrix and return an ECharts tree JSON.

    Args:
        dist_matrix  : symmetric np.ndarray, shape (n, n)
        taxon_names  : ordered list of taxon names — outgroup last

    Returns:
        dict: ECharts-compatible hierarchical tree
              {"name": "root", "children": [...]}
    """
    n = len(taxon_names)

    # scipy linkage expects condensed distance matrix (upper triangle)
    condensed = squareform(dist_matrix)
    Z = linkage(condensed, method='average')  # UPGMA = average linkage

    # root node index is always the last fusion = 2n - 2
    root_index = 2 * n - 2

    return _build_node(root_index, Z, taxon_names, n, matrix)


# --- PRIVATE ---

def _build_node(index: int, Z: np.ndarray, taxon_names: list[str], n: int, matrix: dict) -> dict:
    """
    Recursively build ECharts JSON node from scipy linkage matrix.

    - index < n  → leaf node (real taxon)
    - index >= n → internal node (fusion of two children)

    Args:
        index       : current node index
        Z           : scipy linkage matrix
        taxon_names : ordered taxon name list
        n           : total number of taxa (= number of leaves)

    Returns:
        dict: ECharts node {"name": str, "value": float, "children": [...]}
    """

    # --- LEAF ---
    if index < n:
        is_outgroup = (index == n - 1)  # outgroup is always last
        return {
            "name": taxon_names[index],
            "value": 0.0,
            "characters": matrix.get(taxon_names[index], {}),
            "label": {
                "fontWeight": "bold" if is_outgroup else "normal",
                "color": "#f78166" if is_outgroup else "#212529"
            },
            "children": []
        }

    # --- INTERNAL NODE ---
    # Z rows are 0-indexed from the first fusion
    # internal node `index` corresponds to Z row (index - n)
    row = Z[index - n]

    left_index  = int(row[0])
    right_index = int(row[1])
    distance    = float(row[2])

    left_child = _build_node(left_index, Z, taxon_names, n, matrix)
    right_child = _build_node(right_index, Z, taxon_names, n, matrix)

    return {
        "name": "",           # internal nodes have no name
        "value": round(distance, 4),
        "children": [left_child, right_child]
    }