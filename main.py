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
    # Join Operator and Country tables to get operator name, info, and country name
    operators_data = conn.execute('''
        SELECT
            O.name,
            O.info,
            C.country AS country_name,
            GROUP_CONCAT(A.ability) AS abilities
        FROM Operator AS O
        JOIN Country AS C ON O.country = C.id
        LEFT JOIN Operator_Ability AS OA ON O.id = OA.operator_id
        LEFT JOIN Ability AS A ON OA.ability_id = A.ability_id
        GROUP BY O.id, O.name, O.info, C.country
    ''').fetchall()
    conn.close()

    # Process the fetched data to turn abilities string into a list
    operators_list = []
    for op in operators_data:
        operator_dict = dict(op)
        if operator_dict['abilities']:
            operator_dict['abilities'] = operator_dict['abilities'].split(',')
        else:
            operator_dict['abilities'] = []
        operators_list.append(operator_dict)

    return render_template('operators.html', operators=operators_list) # Pass the data to the template

@app.route('/weapons')
def weapons():
    return render_template('weapons.html')

@app.route('/weapon/<int:weapon_id>')
def weapon_detail(weapon_id):
    # This route will also need to be updated to fetch from the database
    # For now, it remains as is, but you'll apply similar database logic here later.
    return render_template('weapon_detail.html', weapon_id=weapon_id)

if __name__ == '__main__':
    app.run(debug=True)
