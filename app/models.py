from . import db,bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    itineraries = db.relationship('Itinerary', backref='owner', lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
class Itinerary(db.Model):
    __tablename__ = 'itineraries'

    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='itineraries')
    destinations = db.relationship('Destination', backref='itinerary', lazy=True, cascade="all, delete-orphan")

class Destination(db.Model):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    day = db.Column(db.Integer, nullable=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False)