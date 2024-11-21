from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request

db = SQLAlchemy()

class Joke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setup = db.Column(db.String(200), nullable=False)
    delivery = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Joke {self.setup} - {self.delivery}>'


app = Flask(__name__)

# Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/jimmy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi database
db.init_app(app)

# Endpoint untuk mendapatkan lelucon acak
@app.route('/api/joke', methods=['GET'])
def get_joke():
    joke = Joke.query.order_by(db.func.random()).first()
    if joke:
        return jsonify({
            "type": "twopart" if joke.delivery else "single",
            "setup": joke.setup,
            "delivery": joke.delivery or ""
        })
    return jsonify({"error": "No jokes found"}), 404

# Endpoint untuk menambahkan lelucon baru
@app.route('/api/joke', methods=['POST'])
def add_joke():
    data = request.json
    setup = data.get('setup')
    delivery = data.get('delivery', "")
    if not setup:
        return jsonify({"error": "Setup is required"}), 400

    joke = Joke(setup=setup, delivery=delivery)
    db.session.add(joke)
    db.session.commit()
    return jsonify({"message": "Joke added successfully"}), 201

# Endpoint untuk melihat semua lelucon
@app.route('/api/jokes', methods=['GET'])
def list_jokes():
    jokes = Joke.query.all()
    return jsonify([{"id": joke.id, "setup": joke.setup, "delivery": joke.delivery} for joke in jokes])

# Inisialisasi database dengan data awal
@app.cli.command('initdb')
def initdb():
    db.create_all()
    db.session.add(Joke(setup="Why don't scientists trust atoms?", delivery="Because they make up everything!"))
    db.session.add(Joke(setup="Why did the chicken join a band?", delivery="Because it had the drumsticks!"))
    db.session.commit()
    print("Database initialized!")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
