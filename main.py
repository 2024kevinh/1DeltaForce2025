# main
from flask import Flask, render_template, url_for, request
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
    operators_data = conn.execute('''
        SELECT
            O.id,
            O.name,
            O.info,
            C.country AS country_name,
            O.trait,
            O.tactical_gear,
            O.gadget1,
            O.gadget2
        FROM Operator AS O
        JOIN Country AS C ON O.country = C.id
    ''').fetchall()
    conn.close()

    operators_list = []
    for row in operators_data:
        operator = {
            "id": row["id"],
            "name": row["name"],
            "info": row["info"],
            "country_name": row["country_name"],
            "trait": row["trait"],
            "tactical_gear": row["tactical_gear"],
            "gadget1": row["gadget1"],
            "gadget2": row["gadget2"],
            "abilities": []
        }
        if row["trait"]:
            operator["abilities"].append(f"Trait: {row['trait']}")
        if row["tactical_gear"]:
            operator["abilities"].append(f"Tactical Gear: {row['tactical_gear']}")
        if row["gadget1"]:
            operator["abilities"].append(f"Gadget 1: {row['gadget1']}")
        if row["gadget2"]:
            operator["abilities"].append(f"Gadget 2: {row['gadget2']}")
        operators_list.append(operator)

    return render_template('operators.html', operators=operators_list)

@app.route('/weapons')
def weapons():
    categories = [
        {"name": "assault_rifle", "label": "Assault Rifle", "image": "Assault Rifle.png"},
        {"name": "submachine_gun", "label": "Submachine Gun", "image": "Submachine Gun.png"},
        {"name": "shotgun", "label": "Shotgun", "image": "Shotgun.png"},
        {"name": "lightmachine_gun", "label": "Lightmachine Gun", "image": "Lightmachine Gun.png"},
        {"name": "marksman_rifle", "label": "Marksman Rifle", "image": "Marksman Rifle.png"},
        {"name": "sniper_rifle", "label": "Sniper Rifle", "image": "Sniper Rifle.png"},
    ]
    return render_template('weapons.html', categories=categories)

@app.route('/weapon/<int:weapon_id>')
def weapon_detail(weapon_id):
    conn = get_db_connection()
    weapon = conn.execute(
        "SELECT * FROM Weapon WHERE id = ?", (weapon_id,)
    ).fetchone()
    conn.close()
    if weapon is None:
        return render_template('weapon_detail.html', weapon=None)
    return render_template('weapon_detail.html', weapon=weapon)

@app.route('/weapons/<category>')
def weapon_category(category):
    prev_weapon_id = request.args.get('prev_weapon_id')
    conn = get_db_connection()
    # Map category to weapon ID ranges
    category_ranges = {
        "assault_rifle": (1, 19),
        "submachine_gun": (20, 27),
        "shotgun": (28, 31),
        "lightmachine_gun": (32, 35),
        "marksman_rifle": (36, 42),
        "sniper_rifle": (43, 46)
    }
    if category in category_ranges:
        start_id, end_id = category_ranges[category]
        weapons = conn.execute(
            "SELECT * FROM Weapon WHERE id BETWEEN ? AND ?", (start_id, end_id)
        ).fetchall()
    else:
        weapons = []
    conn.close()
    return render_template('weapon_category.html', weapons=weapons, category=category, prev_weapon_id=prev_weapon_id)

@app.route('/operator/<int:operator_id>')
def operator_detail(operator_id):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT
            O.id,
            O.name,
            O.info,
            C.country AS country_name,
            O.trait,
            O.tactical_gear,
            O.gadget1,
            O.gadget2
        FROM Operator AS O
        JOIN Country AS C ON O.country = C.id
        WHERE O.id = ?
    ''', (operator_id,)).fetchone()
    conn.close()

    operator = {
        "id": row["id"],
        "name": row["name"],
        "info": row["info"],
        "country_name": row["country_name"],
        "trait": row["trait"],
        "tactical_gear": row["tactical_gear"],
        "gadget1": row["gadget1"],
        "gadget2": row["gadget2"],
        "abilities": []
    }
    if row["trait"]:
        operator["abilities"].append(f"Trait: {row['trait']}")
    if row["tactical_gear"]:
        operator["abilities"].append(f"Tactical Gear: {row['tactical_gear']}")
    if row["gadget1"]:
        operator["abilities"].append(f"Gadget 1: {row['gadget1']}")
    if row["gadget2"]:
        operator["abilities"].append(f"Gadget 2: {row['gadget2']}")

    return render_template('operator_detail.html', operator=operator)

if __name__ == '__main__':
    app.run(debug=True)
