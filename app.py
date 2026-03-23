from flask import Flask, render_template, request, jsonify
import os

from core.matrix import build_distance_matrix
from core.tree   import build_tree
from core.key    import build_key

app = Flask(__name__)
app.secret_key = os.urandom(24)  # swap for fixed key in production


# --- INDEX ---
@app.route('/')
def index():
    return render_template('index.html')


# --- RUN ANALYSIS ---
@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()

    try:
        # 1. build distance matrix from character states
        dist_matrix, taxon_names = build_distance_matrix(data)

        # 2. run UPGMA and convert to ECharts JSON
        tree_json = build_tree(dist_matrix, taxon_names, data['matrix'])

        # 3. generate dichotomous identification key
        key_json = build_key(data)

        return jsonify({
            'status':     'ok',
            'taxa':       taxon_names,
            'taxa_full':  data['taxa'],
            'characters': data['characters'],
            'matrix':     data['matrix'],
            'phenogram':  tree_json,
            'key':        key_json
        })

    except Exception as e:
        return jsonify({
            'status':  'error',
            'message': str(e)
        }), 400


# --- RESULT ---
@app.route('/result')
def result():
    return render_template('result.html')


# --- RUN ---
if __name__ == '__main__':
    app.run(debug=True)