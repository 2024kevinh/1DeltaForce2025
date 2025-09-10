# main
from flask import Flask, render_template, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('delta__force.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/operators')
def operators():
    conn = get_db_connection()
    # Fetch operators with their abilities (multiple rows per operator possible)
    operators_data = conn.execute('''
        SELECT
            O.id,
            O.name,
            O.info,
            C.country AS country_name,
            A.trait,
            A.tactical_gear,
            A.gadget1,
            A.gadget2
        FROM Operator AS O
        JOIN Country AS C ON O.country = C.id
        LEFT JOIN Operator_Ability AS OA ON O.id = OA.operator_id
        LEFT JOIN Ability AS A ON OA.ability_id = A.ability_id
    ''').fetchall()
    conn.close()

    # Put in to order by op id
    operators_dict = {}
    for row in operators_data:
        op_id = row["id"]

        if op_id not in operators_dict:
            operators_dict[op_id] = {
                "id": row["id"],
                "name": row["name"],
                "info": row["info"],
                "country_name": row["country_name"],
                "trait": None,
                "tactical_gear": None,
                "gadget1": None,
                "gadget2": None,
                "abilities": []
            }

        if row["trait"]:
            operators_dict[op_id]["trait"] = row["trait"]
            operators_dict[op_id]["abilities"].append(f"Trait: {row['trait']}")
        if row["tactical_gear"]:
            operators_dict[op_id]["tactical_gear"] = row["tactical_gear"]
            operators_dict[op_id]["abilities"].append(f"Tactical Gear: {row['tactical_gear']}")
        if row["gadget1"]:
            operators_dict[op_id]["gadget1"] = row["gadget1"]
            operators_dict[op_id]["abilities"].append(f"Gadget 1: {row['gadget1']}")
        if row["gadget2"]:
            operators_dict[op_id]["gadget2"] = row["gadget2"]
            operators_dict[op_id]["abilities"].append(f"Gadget 2: {row['gadget2']}")

    operators_list = list(operators_dict.values())

    return render_template('operators.html', operators=operators_list)

@app.route('/weapons')
def weapons():
    return render_template('weapons.html')

@app.route('/weapon/<int:weapon_id>')
def weapon_detail(weapon_id):
    # weapon details
    return render_template('weapon_detail.html', weapon_id=weapon_id)

@app.route('/weapons/<category>')
def weapon_category(category):
    conn = get_db_connection()
    weapons = conn.execute(
        "SELECT * FROM Weapon WHERE category = ?", (category,)
    ).fetchall()
    conn.close()
    return render_template('weapon_category.html', weapons=weapons, category=category)

if __name__ == '__main__':
    app.run(debug=True)
