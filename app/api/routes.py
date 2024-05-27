from flask import Blueprint, request, jsonify, render_template
from helpers import token_required
from models import db, User, Appointment, appointment_schema, appointments_schema
from datetime import datetime

api = Blueprint('api',__name__, url_prefix='/api')


@api.route('/user_appointment', methods=['GET'])
@token_required
def get_appointments(current_user):
    appointments = Appointment.query.filter_by(customer_token=current_user.token).all()
    response = []

    for appointment in appointments:
        user = User.query.filter_by(token=appointment.customer_token).first()
        appointment_data = {
            'id': appointment.id,
            'vehicle_type': appointment.vehicle_type,
            'appointment_date': appointment.appointment_date,
            'additional_notes': appointment.additional_notes,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number
        }
        response.append(appointment_data)

    return jsonify(response), 200



@api.route('/user_appointment', methods=['POST'])
@token_required
def create_appointment(current_user):
    data = request.json
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    phone_number = data['phone_number']
    vehicle_type = data['vehicle_type']
    additional_notes = data.get('additional_notes', '')
    appointment_date_str = data['appointment_date']

    try:
        # Ensure the format matches exactly without seconds
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d %H:%M')
    except ValueError as e:
        return jsonify({'error': f"Incorrect datetime format: {str(e)}"}), 400

    # Update current user's information if needed
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.email = email
    current_user.phone_number = phone_number

    appointment = Appointment(
        vehicle_type=vehicle_type,
        additional_notes=additional_notes,
        appointment_date=appointment_date,
        customer_token=current_user.token
    )

    db.session.add(current_user)  
    db.session.add(appointment)
    db.session.commit()

    response = appointment_schema.dump(appointment)
    return jsonify(response), 201


@api.route('/user_appointment/<id>', methods=['PUT'])
@token_required
def update_appointment(current_user, id):
    data = request.json
    appointment = Appointment.query.filter_by(id=id, customer_token=current_user.token).first()

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    first_name = data.get('first_name', current_user.first_name)
    last_name = data.get('last_name', current_user.last_name)
    email = data.get('email', current_user.email)
    phone_number = data.get('phone_number', current_user.phone_number)
    vehicle_type = data.get('vehicle_type', appointment.vehicle_type)
    additional_notes = data.get('additional_notes', appointment.additional_notes)
    appointment_date_str = data.get('appointment_date', appointment.appointment_date.strftime('%Y-%m-%d %H:%M'))

    try:
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d %H:%M')
    except ValueError as e:
        return jsonify({'error': f"Incorrect datetime format: {str(e)}"}), 400

    # Update current user's information
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.email = email
    current_user.phone_number = phone_number

    # Update appointment information
    appointment.vehicle_type = vehicle_type
    appointment.additional_notes = additional_notes
    appointment.appointment_date = appointment_date

    db.session.commit()
    response = appointment_schema.dump(appointment)
    return jsonify(response), 200


@api.route('/user_appointment/<id>', methods=['DELETE'])
@token_required
def delete_appointment(current_user, id):
    appointment = Appointment.query.filter_by(id=id, customer_token=current_user.token).first()

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment deleted successfully'}), 200




# @api.route('/cars', methods = ['POST'])
# @token_required
# def create_contact(current_owner_token):
#     make = request.json['make']
#     model = request.json['model']
#     year = request.json['year']
#     color = request.json['color']
#     price = request.json['price']
#     owner_token = current_owner_token.token

#     print(f'BIG TESTER: {current_owner_token.token}')

#     car = Car(make, model, year, color, price, owner_token = owner_token )

#     db.session.add(car)
#     db.session.commit()

#     response = car_schema.dump(car)
#     return jsonify(response)

# @api.route('/cars', methods = ['GET'])
# @token_required
# def get_contact(current_owner_token):
#     owner = current_owner_token.token
#     cars = Car.query.filter_by(owner_token = owner).all()
#     response = cars_schema.dump(cars)
#     return jsonify(response)

# @api.route('/cars/<id>', methods = ['GET'])
# @token_required
# def get_car_two(current_owner_token, id):
#     fan = current_owner_token.token
#     if fan == current_owner_token.token:
#         car = Car.query.get(id)
#         response = car_schema.dump(car)
#         return jsonify(response)
#     else:
#         return jsonify({"message": "Valid Token Required"}),401

# # UPDATE endpoint
# @api.route('/cars/<id>', methods = ['POST','PUT'])
# @token_required
# def update_contact(current_owner_token,id):
#     car = Car.query.get(id) 
#     car.make = request.json['make']
#     car.model = request.json['model']
#     car.year = request.json['year']
#     car.color = request.json['color']
#     car.price = request.json['price']
#     car.owner_token = current_owner_token.token

#     db.session.commit()
#     response = car_schema.dump(car)
#     return jsonify(response)


# # DELETE car ENDPOINT
# @api.route('/cars/<id>', methods = ['DELETE'])
# @token_required
# def delete_car(current_owner_token, id):
#     car = Car.query.get(id)
#     db.session.delete(car)
#     db.session.commit()
#     response = car_schema.dump(car)
#     return jsonify(response)



