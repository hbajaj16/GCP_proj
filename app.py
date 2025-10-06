from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)

# --- Database Configuration ---
# Replace placeholders with your actual Cloud SQL credentials and connection info
# For a private IP or Cloud SQL Proxy connection:
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://<DB_USER>:<DB_PASSWORD>@/<DB_NAME>?unix_socket=/cloudsql/<INSTANCE_CONNECTION_NAME>'
# For public IP (ensure your VM's IP is whitelisted):
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{database}'.format(
    user=os.environ.get('DB_USER', 'your_db_user'),
    password=os.environ.get('DB_PASS', 'your_db_password'),
    host=os.environ.get('DB_HOST', '127.0.0.1'), # Use the public or private IP of your Cloud SQL instance
    database=os.environ.get('DB_NAME', 'your_db_name')
)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Model (Simple Table) ---
class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    message = db.Column(db.String(100), default='Hello from VM')

# --- Routes ---
@app.route('/')
def home():
    # Create the table if it doesn't exist
    with app.app_context():
        db.create_all() 
        
    # Record a new visit
    new_visit = Visit()
    db.session.add(new_visit)
    db.session.commit()

    # Get the last 10 visits
    visits = Visit.query.order_by(Visit.timestamp.desc()).limit(10).all()
    
    visit_list = [{
        'id': v.id, 
        'timestamp': v.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
        'message': v.message
    } for v in visits]

    return jsonify({
        'status': 'success',
        'message': 'Visit recorded.',
        'recent_visits': visit_list
    })

# --- Run the application ---
if __name__ == '__main__':
    # Use Gunicorn or a similar WSGI server for production, but this is fine for a demo
    app.run(host='0.0.0.0', port=8080)
