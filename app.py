from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from config import Config
from api.routes import api_bp
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/timeline')
def timeline():
    """Timeline view route"""
    return render_template('timeline.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure data directories exist
    os.makedirs('data/analysis_results', exist_ok=True)
    
    # Run the application
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )