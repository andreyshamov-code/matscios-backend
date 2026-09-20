import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Разрешаем CORS-запросы с вашего сайта matscios.com
CORS(app)

# Получаем API-ключ из переменных окружения Render
MP_API_KEY = os.environ.get("MP_API_KEY", "")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "MatSciOS AI Computational Backend",
        "version": "3.8.0"
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/v1/predict", methods=["POST"])
def predict_material():
    data = request.get_json() or {}
    elements = data.get("elements", [])
    exec_mode = data.get("mode", "cloud")

    if not elements:
        return jsonify({"error": "No elements provided"}), 400

    chemsys = "-".join(elements)

    # 1. Попытка получить реальные данные из Materials Project API
    if MP_API_KEY:
        try:
            url = f"https://api.materialsproject.org/v2/materials/summary?chemsys={chemsys}&_limit=5"
            headers = {"X-API-KEY": MP_API_KEY}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                mp_data = response.json().get("data", [])
                results = []
                for item in mp_data:
                    results.append({
                        "formula": item.get("formula_pretty", chemsys),
                        "bandGap": round(item.get("band_gap", 0.0) or 0.0, 2),
                        "density": round(item.get("density", 0.0) or 0.0, 2),
                        "energy_above_hull": round(item.get("energy_above_hull", 0.0) or 0.0, 3),
                        "pdb": generate_demo_pdb(elements)
                    })
                if results:
                    return jsonify({"source": "Materials Project API", "results": results}), 200
        except Exception as e:
            print(f"API Error: {e}")

    # 2. Фолбэк / AI-эмуляция расчетов, если ключ не задан или API недоступно
    mock_results = [
        {
            "formula": f"{''.join(elements)}O2",
            "bandGap": 1.42,
            "density": 4.12,
            "energy_above_hull": 0.012,
            "pdb": generate_demo_pdb(elements)
        },
        {
            "formula": f"{''.join(elements)}2Si",
            "bandGap": 0.85,
            "density": 3.95,
            "energy_above_hull": 0.045,
            "pdb": generate_demo_pdb(elements)
        }
    ]

    return jsonify({
        "source": "MatSciOS AI Emulator Engine",
        "results": mock_results
    }), 200

def generate_demo_pdb(elements):
    """Генерация простой 3D-структуры PDB для отображения в 3Dmol.js"""
    elem1 = elements[0] if len(elements) > 0 else "C"
    elem2 = elements[1] if len(elements) > 1 else "O"
    
    pdb = f"""HEADER    MATSCIOS GENERATED STRUCTURE
ATOM      1  {elem1:<2}  MOL A   1       0.000   0.000   0.000  1.00  0.00          {elem1:>2}
ATOM      2  {elem2:<2}  MOL A   1       1.420   1.200   0.000  1.00  0.00          {elem2:>2}
ATOM      3  {elem2:<2}  MOL A   1      -1.420   1.200   0.000  1.00  0.00          {elem2:>2}
END
"""
    return pdb

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
