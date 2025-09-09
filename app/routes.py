import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app
from .models import db,User, Itinerary, Destination
from .auth_decorator import token_required
import json
import google.generativeai as genai

main_bp = Blueprint('main', __name__)

@main_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'message': 'MISSING FEILDS!'}), 400
    if User.query.filter_by(email=data['email']).first() or User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists!'}), 400
    
    try:
        new_user = User(username=data['username'], password=data['password'],email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New User registered successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed!', 'error': str(e)}), 500
    
@main_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Could not verify'}), 401
    
    user = User.query.filter_by(email=data['email']).first()
    if user or user.check_password(data['password']):
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Login failed! Invalid email or password.'}), 401

@main_bp.route('/itineraries', methods=['POST'])
@token_required
def creaate_itinerary(current_user):
    data = request.get_json()

    required_fields = ['trip_name','city','duration_days','interests'] 
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'MISSING fields!Required: trip_name, city, duration_days, interests'}), 400
    try:
        new_itinerary = Itinerary(trip_name=data['trip_name'], user_id = current_user.id)
        db.session.add(new_itinerary)
        db.session.commit()

        genai.configure(api_key=current_app.config['API_KEY'])
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (
            f"Create a travel itinerary for {data['city']} for {data['duration_days']} days, with a focus on {data['interests']}. "
        "Return ONLY a valid JSON list of objects. Each object must have keys: "
        "'day' (int), 'location_name' (string), and 'description' (string, max 50 words). "
        "Do not add any intro text, markdown formatting like ```json, or trailing ```."
        )

        response = model.generate_content(prompt)
        clean_text = response.text.strip().replace("```json","").replace("```","").strip()
        destination_list = json.loads(clean_text)

        all_dests = []
        for item in destination_list:
            new_dest = Destination(
                location_name=item['location_name'],
                notes=item['description'],
                day=item['day'],
                itinerary_id=new_itinerary.id
            )
            db.session.add(new_dest)
            all_dests.append(new_dest)

        db.session.commit()
        dest_output = [{'id':d.id,'location_name':d.location_name,'notes':d.notes, 'day':d.day} for d in all_dests]
        return jsonify({
            'message': 'New Itinerary created successfully!',
            'itinerary': {
                'itinerary_id': new_itinerary.id,
                'trip_name': new_itinerary.trip_name,
                'destinations': dest_output
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Itinerary creation failed!', 'error': str(e)}), 500
    


@main_bp.route('/itineraries', methods=['GET'])
@token_required
def get_itineraries(current_user):
    
    output = []
    for itinerary in current_user.itineraries:
        dest_list = [{'destination_id':d.id,'location_name':d.location_name,'notes':d.notes} for d in itinerary.destinations]
        itinerary_data = {
            'itinerary_id': itinerary.id,
            'trip_name': itinerary.trip_name,
            'destinations': dest_list
        }
        output.append(itinerary_data)
    return jsonify({'itineraries': output}), 200

@main_bp.route('/itineraries/<int:trip_id>', methods=['GET'])
@token_required
def get_itinerary(current_user, trip_id):
    itinerary = Itinerary.query.get(trip_id)
    if not itinerary:
        return jsonify({'message': 'Itinerary not found!'}), 404
    
    if itinerary.user_id != current_user.id:
        return jsonify({'message': 'Forbidden: You do not have access to this itinerary'}), 403
    dest_list = [{'destination_id':d.id,'location_name':d.location_name,'notes':d.notes,'day':d.day} for d in itinerary.destinations]
    itinerary_data = {
        'itinerary_id': itinerary.id,
        'trip_name': itinerary.trip_name,
        'destinations': dest_list
    }
    return jsonify({'itinerary': itinerary_data}), 200

@main_bp.route('/itineraries/<int:trip_id>', methods=['DELETE'])
@token_required
def delete_itinerary(current_user, trip_id):
    itinerary = Itinerary.query.get(trip_id)
    if not itinerary:
        return jsonify({'message': 'Itinerary not found!'}), 404
    
    if itinerary.user_id != current_user.id:
        return jsonify({'message': 'Forbidden: You do not have access to this itinerary'}), 403
    try:
        db.session.delete(itinerary)
        db.session.commit()
        return jsonify({'message': 'Itinerary deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete itinerary!', 'error': str(e)}), 500
    
@main_bp.route('/itineraries/<int:trip_id>', methods=['PUT'])
@token_required
def update_tripName(current_user, trip_id):
    itinerary = Itinerary.query.get(trip_id)
    if not itinerary:
        return jsonify({'message': 'Itinerary not found!'}), 404
    
    if itinerary.user_id != current_user.id:
        return jsonify({'message': 'Forbidden: You do not have access to this itinerary'}), 403
    
    data = request.get_json()
    new_name = data.get('trip_name')

    if not new_name:
        return jsonify({'message': 'MISSING trip_name in request body'}), 400
    
    itinerary.trip_name = new_name
    db.session.commit()
    return jsonify({'message': 'Itinerary name updated successfully!'}), 200