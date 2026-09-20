import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MP_API_KEY = os.environ.get("MP_API_KEY", "")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "MatSciOS AI Computational Backend",
        "version": "3.8.1"
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/v1/predict", methods=["POST"])
def predict_material():
    data = request.get_json() or {}
    elements = data.get("elements", [])
    
    if not elements:
        return jsonify({"error": "No elements provided"}), 400

    # Генерируем тестовые фазы с корректной PDB 3D-структурой
    e1 = elements[0] if len(elements) > 0 else "Li"
    e2 = elements[1] if len(elements) > 1 else "O"
    
    mock_results = [
        {
            "formula": f"{e1}{e2}2",
            "bandGap": 1.42,
            "density": 4.12,
            "energy_above_hull": 0.012,
            "pdb": generate_valid_pdb(e1, e2)
        },
        {
            "formula": f"{e1}{e2}Si",
            "bandGap": 0.85,
            "density": 3.95,
            "energy_above_hull": 0.045,
            "pdb": generate_valid_pdb(e1, "Si")
        }
    ]

    return jsonify({
        "source": "MatSciOS AI Engine",
        "results": mock_results
    }), 200

def generate_valid_pdb(elem1, elem2):
    """Генерация строго валидного PDB формата для 3Dmol.js"""
    pdb_lines = [
        "HEADER    MATSCIOS 3D CRYSTAL STRUCTURE",
        f"ATOM      1  {elem1:<2}  MOL A   1       0.000   0.000   0.000  1.00  0.00          {elem1:>2}",
        f"ATOM      2  {elem2:<2}  MOL A   1       1.500   0.000   0.000  1.00  0.00          {elem2:>2}",
        f"ATOM      3  {elem2:<2}  MOL A   1      -0.750   1.300   0.000  1.00  0.00          {elem2:>2}",
        f"ATOM      4  {elem1:<2}  MOL A   1       0.000   0.000   1.500  1.00  0.00          {elem1:>2}",
        "CONECT    1    2    3    4",
        "END"
    ]
    return "\n".join(pdb_lines)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
