import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Координатная сетка для построения 3D-ячейки кристаллов
BASE_POSITIONS = [
    (0.000, 0.000, 0.000),
    (1.420, 1.200, 0.000),
    (-1.420, 1.200, 0.000),
    (0.000, 2.400, 1.200),
    (1.420, -1.200, 1.200),
    (-1.420, -1.200, 1.200),
    (2.840, 0.000, 0.000),
    (-2.840, 0.000, 0.000),
]

def generate_dynamic_pdb(elements):
    """Генерация валидной PDB-структуры для произвольного набора элементов."""
    if not elements:
        elements = ["Li", "O"]

    pdb_lines = ["HEADER    MATSCIOS DYNAMIC CRYSTAL STRUCTURE"]
    atom_id = 1

    for i, pos in enumerate(BASE_POSITIONS):
        elem = elements[i % len(elements)]
        x, y, z = pos
        line = f"ATOM  {atom_id:>5}  {elem:<2}  MOL A   1     {x:>7.3f} {y:>7.3f} {z:>7.3f}  1.00  0.00          {elem:>2}"
        pdb_lines.append(line)
        atom_id += 1

    pdb_lines.append("CONECT    1    2    3    4")
    pdb_lines.append("END")
    return "\n".join(pdb_lines)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "MatSciOS AI Multi-Physics Backend",
        "version": "3.9.0"
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/v1/predict", methods=["POST"])
def predict_material():
    data = request.get_json() or {}
    elements = data.get("elements", [])
    preset = data.get("preset", "general")

    if not elements:
        elements = ["Li", "Fe", "O"]

    e_str = "".join(elements[:3])
    
    mock_results = [
        {
            "formula": f"{e_str}O2",
            "bandGap": round(random.uniform(0.1, 3.5), 2),
            "density": round(random.uniform(2.5, 8.9), 2),
            "energy_above_hull": 0.012,
            "pdb": generate_dynamic_pdb(elements)
        },
        {
            "formula": f"{e_str}2Si",
            "bandGap": round(random.uniform(0.0, 2.1), 2),
            "density": round(random.uniform(3.0, 9.5), 2),
            "energy_above_hull": 0.038,
            "pdb": generate_dynamic_pdb(list(reversed(elements)))
        }
    ]

    return jsonify({
        "source": "MatSciOS AI Engine",
        "preset": preset,
        "results": mock_results
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
