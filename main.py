# main.py

from flask import (
    Flask, render_template, url_for,
    request, redirect, session, flash, g
)
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'  # Replace with a secure key in production


def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect('delta__force.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.before_request
def load_logged_in_user():
    """Load the logged-in user into the Flask global context (g)."""
    user_email = session.get('user')
    if user_email:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM logins WHERE email = ?',
            (user_email,)
        ).fetchone()
        conn.close()
        g.user = user
    else:
        g.user = None


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/operators')
def operators():
    """Display all operators."""
    conn = get_db_connection()
    operators_data = conn.execute(
        '''
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
        '''
    ).fetchall()
    conn.close()

    # Build a list of operator dictionaries
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
            operator["abilities"].append(
                f"Tactical Gear: {row['tactical_gear']}"
            )
        if row["gadget1"]:
            operator["abilities"].append(f"Gadget 1: {row['gadget1']}")
        if row["gadget2"]:
            operator["abilities"].append(f"Gadget 2: {row['gadget2']}")
        operators_list.append(operator)

    return render_template('operators.html', operators=operators_list)


@app.route('/weapons')
def weapons():
    """Display weapon categories."""
    categories = [
        {
            "name": "assault_rifle",
            "label": "Assault Rifle",
            "image": "Assault Rifle.png"
        },
        {
            "name": "submachine_gun",
            "label": "Submachine Gun",
            "image": "Submachine Gun.png"
        },
        {
            "name": "shotgun",
            "label": "Shotgun",
            "image": "Shotgun.png"
        },
        {
            "name": "lightmachine_gun",
            "label": "Lightmachine Gun",
            "image": "Lightmachine Gun.png"
        },
        {
            "name": "marksman_rifle",
            "label": "Marksman Rifle",
            "image": "Marksman Rifle.png"
        },
        {
            "name": "sniper_rifle",
            "label": "Sniper Rifle",
            "image": "Sniper Rifle.png"
        },
    ]
    return render_template('weapons.html', categories=categories)


@app.route('/weapon/<int:weapon_id>')
def weapon_detail(weapon_id):
    """
    Display details for a specific weapon, including its ammo types.
    """
    conn = get_db_connection()
    weapon = conn.execute(
        "SELECT * FROM Weapon WHERE id = ?",
        (weapon_id,)
    ).fetchone()

    # Get all ammo types for this weapon
    ammo_rows = conn.execute(
        '''
        SELECT A.name, A.ammo_info
        FROM Ammo AS A
        JOIN Weapon_Ammo AS WA ON WA.ammo_id = A.id
        WHERE WA.weapon_id = ?
        ''',
        (weapon_id,)
    ).fetchall()
    conn.close()

    ammo_list = [
        {"name": row["name"], "info": row["ammo_info"]}
        for row in ammo_rows
    ]

    if weapon is None:
        return render_template('weapon_detail.html', weapon=None, ammo_list=[])
    return render_template('weapon_detail.html',
                           weapon=weapon,
                           ammo_list=ammo_list)


@app.route('/weapons/<category>')
def weapon_category(category):
    """
    Display all weapons in a specific category.
    """
    prev_weapon_id = request.args.get('prev_weapon_id')
    conn = get_db_connection()

    # Define weapon ID ranges for each category
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
            "SELECT * FROM Weapon WHERE id BETWEEN ? AND ?",
            (start_id, end_id)
        ).fetchall()
    else:
        weapons = []
    conn.close()

    return render_template(
        'weapon_category.html',
        weapons=weapons,
        category=category,
        prev_weapon_id=prev_weapon_id
    )


@app.route('/operator/<int:operator_id>')
def operator_detail(operator_id):
    """
    Display details for a specific operator.
    """
    conn = get_db_connection()
    row = conn.execute(
        '''
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
        ''',
        (operator_id,)
    ).fetchone()
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM Logins WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()

        # NOTE: For production, use hashed passwords!
        if user and password == user['password']:
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password', 'danger')

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    """
    Handle user logout.
    """
    session.pop('user', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO logins (name, email, password, role) '
                'VALUES (?, ?, ?, ?)',
                (name, email, password, role)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/damage_simulator', methods=['GET', 'POST'])
def damage_simulator():
    """
    Simulate weapon damage based on weapon, hit part, and distance.
    """
    categories = [
        {"name": "Assault Rifle", "label": "Assault Rifle"},
        {"name": "Submachine Gun", "label": "Submachine Gun"},
        {"name": "Shotgun", "label": "Shotgun"},
        {"name": "Light Machine Gun", "label": "Light Machine Gun"},
        {"name": "Marksman Rifle", "label": "Marksman Rifle"},
        {"name": "Sniper Rifle", "label": "Sniper Rifle"},
    ]

    conn = get_db_connection()
    all_weapons = []
    for cat in categories:
        weapons = conn.execute(
            '''SELECT id, name, damage FROM Weapon
            WHERE category = ?''', (cat["name"],)
        ).fetchall()
        all_weapons.append({
            "category": cat["label"],
            "weapons": [dict(w) for w in weapons]
        })
    conn.close()

    result = None
    weapon_id = None
    selected_weapon = None
    selected_category = None

    if request.method == 'POST':
        weapon_id = request.form.get('weapon')
        if (
            weapon_id and
            'hit_part' in request.form and
            'distance' in request.form
        ):
            weapon_id = int(weapon_id)
            for group in all_weapons:
                for w in group['weapons']:
                    if w['id'] == weapon_id:
                        selected_weapon = w
                        selected_category = group['category']
                        break
                if selected_weapon:
                    break

            hit_part = request.form['hit_part']
            distance = int(request.form['distance'])

            base_damage = selected_weapon['damage']
            if hit_part == 'head':
                base_damage = int(base_damage * 1.8)
            elif hit_part == 'legs' or hit_part == 'limbs':
                base_damage = int(base_damage * 0.9)

            # Reduce damage by 10% for every 50m, up to 4 steps (max 200m)
            reduction = min(distance // 50, 6)
            final_damage = int(base_damage * (0.9 ** reduction))
            remaining_hp = max(100 - final_damage, 0)

            result = {
                'weapon': selected_weapon['name'],
                'category': selected_category,
                'hit_part': hit_part.title(),
                'distance': distance,
                'damage': final_damage,
                'remaining_hp': remaining_hp
            }

    return render_template(
        'damage_simulator.html',
        all_weapons=all_weapons,
        result=result
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
