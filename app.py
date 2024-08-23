from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector  # Import this if you're using MySQL

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database configuration (if applicable)
db_config = {
    'host': 'localhost',
    'user': 'energy_user',
    'password': 'password123',
    'database': 'rural_energy_app'
}

# Initialize database connection and create table if not exists (if applicable)
def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Survey (
            id INT AUTO_INCREMENT PRIMARY KEY,
            location VARCHAR(255) NOT NULL,
            population INT NOT NULL,
            energy_source VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# Emission Factors (if applicable)
EMISSION_FACTORS = {
    'wood': 0.42,
    'charcoal': 0.90,
    'kerosene': 2.40
}

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_data():
    if request.method == 'POST':
        location = request.form['location']
        population = request.form['population']
        energy_source = request.form['energy_source']

        # Save data to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Survey (location, population, energy_source) VALUES (%s, %s, %s)",
                       (location, population, energy_source))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Data submitted successfully!')
        return redirect(url_for('index'))
    return render_template('submit_data.html')

@app.route('/dashboard')
def dashboard():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Survey")
    surveys = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', surveys=surveys)

@app.route('/eco_calculator', methods=['GET', 'POST'])
def eco_calculator():
    result = None
    if request.method == 'POST':
        wood_usage = float(request.form['wood'])
        charcoal_usage = float(request.form['charcoal'])
        kerosene_usage = float(request.form['kerosene'])

        # Calculate carbon footprint
        wood_footprint = wood_usage * EMISSION_FACTORS['wood']
        charcoal_footprint = charcoal_usage * EMISSION_FACTORS['charcoal']
        kerosene_footprint = kerosene_usage * EMISSION_FACTORS['kerosene']
        
        total_footprint = wood_footprint + charcoal_footprint + kerosene_footprint

        result = {
            'wood_footprint': wood_footprint,
            'charcoal_footprint': charcoal_footprint,
            'kerosene_footprint': kerosene_footprint,
            'total_footprint': total_footprint
        }

    return render_template('eco_calculator.html', result=result)

# Add this route for the map view
@app.route('/map')
def map_view():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
