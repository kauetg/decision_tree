/* ============================================
   decision_tree — main.js
   ============================================ */

// --- STATE ---
let state = {
    characters: [],  // [{ name: str, states: [str] }]
    taxa: [],        // [{ name: str, outgroup: bool }]
    matrix: {}       // { taxon_name: { char_name: state } }
};

const N_DEFAULT_CHARS = 4;
const N_DEFAULT_TAXA  = 4;

// --- INIT ---
document.addEventListener('DOMContentLoaded', () => {
    // guard — only run on index page
    if (!document.getElementById('characters-container')) return;

    for (let i = 0; i < N_DEFAULT_CHARS; i++) addCharacterRow();
    for (let i = 0; i < N_DEFAULT_TAXA;  i++) addTaxonRow();

    document.getElementById('add-character').addEventListener('click', addCharacterRow);
    document.getElementById('add-taxon').addEventListener('click', addTaxonRow);
    document.getElementById('btn-save').addEventListener('click', saveJSON);
    document.getElementById('btn-load').addEventListener('click', () => document.getElementById('load-file-input').click());
    document.getElementById('load-file-input').addEventListener('change', loadJSON);
    document.getElementById('btn-run').addEventListener('click', runAnalysis);
});

// --- CHARACTER ROWS ---
function addCharacterRow(name = '', states = '') {
    const container = document.getElementById('characters-container');
    const row = document.createElement('div');
    row.className = 'row input-row align-items-center';
    row.innerHTML = `
        <div class="col-5">
            <input type="text" class="form-control form-control-sm char-name"
                   placeholder="e.g. colony_shape" value="${name}">
        </div>
        <div class="col-6">
            <input type="text" class="form-control form-control-sm char-states"
                   placeholder="e.g. branching, massive, encrusting" value="${states}">
        </div>
        <div class="col-1 text-center">
            <button class="btn-remove" onclick="removeRow(this)">
                <i class="bi bi-x-circle"></i>
            </button>
        </div>
    `;
    container.appendChild(row);
    row.querySelectorAll('input').forEach(i => i.addEventListener('input', refreshMatrix));
}

// --- TAXON ROWS ---
function addTaxonRow(name = '', isOutgroup = false) {
    const container = document.getElementById('taxa-container');
    const row = document.createElement('div');
    row.className = 'row input-row align-items-center';
    row.innerHTML = `
        <div class="col-5">
            <input type="text" class="form-control form-control-sm taxon-name"
                   placeholder="e.g. Acropora palmata" value="${name}">
        </div>
        <div class="col-6">
            <div class="form-check form-check-inline">
                <input class="form-check-input outgroup-radio" type="radio"
                       name="outgroup" value="${name}" ${isOutgroup ? 'checked' : ''}>
                <label class="form-check-label">outgroup</label>
            </div>
        </div>
        <div class="col-1 text-center">
            <button class="btn-remove" onclick="removeRow(this)">
                <i class="bi bi-x-circle"></i>
            </button>
        </div>
    `;
    container.appendChild(row);
    row.querySelector('.taxon-name').addEventListener('input', (e) => {
        // keep radio value in sync with taxon name
        row.querySelector('.outgroup-radio').value = e.target.value;
        refreshMatrix();
    });
    row.querySelector('.outgroup-radio').addEventListener('change', refreshMatrix);
}

// --- REMOVE ROW ---
function removeRow(btn) {
    btn.closest('.input-row').remove();
    refreshMatrix();
}

// --- READ STATE FROM DOM ---
function readStateFromDOM() {
    // characters
    state.characters = [];
    document.querySelectorAll('#characters-container .input-row').forEach(row => {
        const name   = row.querySelector('.char-name').value.trim();
        const raw    = row.querySelector('.char-states').value;
        const states = raw.split(',').map(s => s.trim()).filter(Boolean);
        if (name) state.characters.push({ name, states });
    });

    // taxa
    state.taxa = [];
    const outgroupVal = document.querySelector('input[name="outgroup"]:checked')?.value || '';
    document.querySelectorAll('#taxa-container .input-row').forEach(row => {
        const name     = row.querySelector('.taxon-name').value.trim();
        const outgroup = (name && name === outgroupVal);
        if (name) state.taxa.push({ name, outgroup });
    });
}

// --- REFRESH MATRIX ---
function refreshMatrix() {
    readStateFromDOM();

    const container = document.getElementById('matrix-container');

    if (state.characters.length === 0 || state.taxa.length === 0) {
        container.innerHTML = `
            <p class="text-muted matrix-placeholder">
                <i class="bi bi-arrow-up-circle"></i>
                Fill in characters and taxa above to generate the matrix.
            </p>`;
        return;
    }

    // preserve existing selections
    const saved = {};
    container.querySelectorAll('select[data-taxon][data-char]').forEach(sel => {
        const key = `${sel.dataset.taxon}||${sel.dataset.char}`;
        saved[key] = sel.value;
    });

    // build table
    let html = `<div class="table-responsive">
        <table class="table table-bordered matrix-table">
            <thead><tr>
                <th>taxon</th>`;

    state.characters.forEach(c => {
        html += `<th>${c.name || '—'}</th>`;
    });
    html += `</tr></thead><tbody>`;

    state.taxa.forEach(t => {
        const rowClass = t.outgroup ? 'outgroup-row' : '';
        html += `<tr class="${rowClass}">
            <td>${t.name}${t.outgroup ? ' <span class="badge text-bg-primary" style="font-size:0.65rem">outgroup</span>' : ''}</td>`;

        state.characters.forEach(c => {
            const key = `${t.name}||${c.name}`;
            const prev = saved[key] || '';

            if (c.states.length === 0) {
                html += `<td><input type="text" class="form-control form-control-sm"
                            data-taxon="${t.name}" data-char="${c.name}"
                            value="${prev}" placeholder="—"></td>`;
            } else {
                html += `<td><select class="form-select form-select-sm"
                            data-taxon="${t.name}" data-char="${c.name}">
                            <option value="">—</option>`;
                c.states.forEach(s => {
                    html += `<option value="${s}" ${prev === s ? 'selected' : ''}>${s}</option>`;
                });
                html += `</select></td>`;
            }
        });
        html += `</tr>`;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
}

// --- BUILD MATRIX PAYLOAD ---
function buildMatrixPayload() {
    readStateFromDOM();
    const matrix = {};
    document.querySelectorAll('#matrix-container select, #matrix-container input[data-taxon]').forEach(el => {
        const taxon = el.dataset.taxon;
        const char  = el.dataset.char;
        if (!matrix[taxon]) matrix[taxon] = {};
        matrix[taxon][char] = el.value;
    });
    return {
        characters: state.characters,
        taxa: state.taxa,
        matrix
    };
}

// --- SAVE JSON ---
function saveJSON() {
    const payload = buildMatrixPayload();
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'decision_tree_session.json';
    a.click();
    URL.revokeObjectURL(url);
}

// --- LOAD EXAMPLE ---
function loadExample(filename) {
    fetch(`/static/test_data/${filename}`)
        .then(res => res.json())
        .then(data => restoreFromJSON(data))
        .catch(err => {
            console.error(err);
            alert('Could not load example dataset.');
        });
}
function loadJSON(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            restoreFromJSON(data);
        } catch {
            alert('Invalid JSON file.');
        }
    };
    reader.readAsText(file);
    event.target.value = ''; // reset so same file can be reloaded
}

function restoreFromJSON(data) {
    // clear containers
    document.getElementById('characters-container').innerHTML = '';
    document.getElementById('taxa-container').innerHTML = '';

    // temporarily remove input listeners to avoid multiple refreshMatrix calls
    data.characters.forEach(c => addCharacterRow(c.name, c.states.join(', ')));
    data.taxa.forEach(t => addTaxonRow(t.name, t.outgroup));

    // force matrix rebuild synchronously
    refreshMatrix();

    // restore matrix selections after matrix is in the DOM
    document.querySelectorAll('#matrix-container select, #matrix-container input[data-taxon]').forEach(el => {
        const val = data.matrix?.[el.dataset.taxon]?.[el.dataset.char];
        if (val !== undefined) el.value = val;
    });
}

// --- RUN ANALYSIS ---
function runAnalysis() {
    const payload = buildMatrixPayload();

    // basic validation
    if (payload.characters.length < 2) {
        alert('Add at least 2 characters.'); return;
    }
    if (payload.taxa.length < 3) {
        alert('Add at least 3 taxa (including outgroup).'); return;
    }
    if (!payload.taxa.some(t => t.outgroup)) {
        alert('Select one outgroup taxon.'); return;
    }

    // POST to Flask — /run route (to be implemented)
    fetch('/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(result => {
        console.log('🌿 /run response:', JSON.stringify(result, null, 2));
        // store result and redirect to result page
        sessionStorage.setItem('dt_result', JSON.stringify(result));
        window.location.href = '/result';
    })
    .catch(err => {
        console.error(err);
        alert('Error communicating with server.');
    });
}