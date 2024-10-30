from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods= ['GET', 'POST'])
def messages():

    if request.method == 'GET':
        records = []
        for record in Message.query.order_by(Message.created_at.asc()).all():
            record_dict = record.to_dict()
            records.append(record_dict)

        response = make_response(
            records,
            200
        )

        return response
    
    elif request.method == 'POST':
        data = request.get_json()

        new_message = Message(
            body=data.get("body"),
            username=data.get("username"),
        )

        db.session.add(new_message)
        db.session.commit()

        record_dict = new_message.to_dict()

        response = make_response(
            record_dict,
            201
        )

        return response

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()

    if message == None:
        response_body = {
            "message": "This message dos not exist in tour database. Please try again."
        }
        response = make_response(response_body, 404)

        return response

    if request.method == 'GET':
        message_dict = message.to_dict()

        response = make_response(
            message_dict,
            200
        )

        return response
    
    elif request.method == 'PATCH':
        data = request.get_json()
        if not data:
            return make_response({"message": "No data provided for update."}, 400)

        # Update attributes
        for attr, value in data.items():
            if hasattr(message, attr):
                setattr(message, attr, value)

        db.session.commit()

        return make_response(message.to_dict(), 200)

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response({"message": "Message deleted successfully."}, 200)

if __name__ == '__main__':
    app.run(port=5555)
