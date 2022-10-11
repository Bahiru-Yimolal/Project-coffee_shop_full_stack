import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES
'''
GET /drinks:
         -public endpoint
         -contain only the drink.short() data representation
         -returns status code 200 and json {"success": True, 
          "drinks": drinks} where drinks is the list of drinks
          or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def retrieve_drinks():
    drink = Drink.query.order_by(Drink.id)
    drinks = drink.all()
    num_question_type = drink.count()
    if not num_question_type == 0:
        all_drinks = [all_drink.short() for all_drink in drinks]
        return jsonify({
            "success": True,
            "drinks": all_drinks
        })
    else:
        abort(404)
'''
GET /drinks-detail
        -require the 'get:drinks-detail' permission
        -contain the drink.long() data representation
        -returns status code 200 and json {"success": True, "drinks": drinks} 
         where drinks is the list of drinks 
         or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drink_detail(payload):
    drink = Drink.query.order_by(Drink.id)
    drinks = drink.all()
    num_question_type = drink.count()
    if not num_question_type == 0:
        all_drinks = [all_drink.long() for all_drink in drinks]
        return jsonify({
            "success": True,
            "drinks": all_drinks
        })
    else:
        abort(404)
'''
POST /drinks
        -create a new row in the drinks table
        -require the 'post:drinks' permission
        -contain the drink.long() data representation
        -returns status code 200 and json {"success": True, "drinks": drink} 
         where drink an array containing only the newly created drink
         or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    if body['title'] and json.dumps(body['recipe']):
            add_new_drink = Drink(title=body['title'],
            recipe=json.dumps(body['recipe']))
            if add_new_drink is None:
                abort(404)
            add_new_drink.insert()
            long_drink = add_new_drink.long()
            return jsonify({
                "success": True,
                "drinks":long_drink,
            })
    else:
            abort(422)

'''
PATCH /drinks/<id>
        -where <drink_id> is the existing model drink_id
        -respond with a 404 error if <drink_id> is not found
        -update the corresponding row for <drink_id>
        -equire the 'patch:drinks' permission
        -contain the drink.long() data representation
        -returns status code 200 and json {"success": True, "drinks": drink} 
         where drink an array containing only the updated drink
         or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload,drink_id):
    body = request.get_json()
    try:
        fetch_update_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if fetch_update_drink is None:
            abort(404)
        if body['title'] and json.dumps(body['recipe']):
            fetch_update_drink.title = body['title'] 
            fetch_update_drink.recipe = json.dumps(body['recipe'])
        fetch_update_drink.update()
        long_drink = fetch_update_drink.long()
        return jsonify({
            "success": True, 
            "drinks": [long_drink]})
    except:
            abort(400)
'''
DELETE /drinks/<drink_id>
        -where <drink_id> is the existing model id
        -respond with a 404 error if <drink_id> is not found
        -delete the corresponding row for <drink_id>
        -require the 'delete:drinks' permission
        -returns status code 200 and json {"success": True, "delete": drink_id} 
          where id is the id of the deleted record
          or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,drink_id):
    try:
        fetch_delete_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if not fetch_delete_drink is None:
             fetch_delete_drink.delete()
             return jsonify({
                "success": True, 
                "delete": drink_id})
        else:
                abort(422)
    except:
            abort(404)

# Error Handling
"""
error handlers for AuthError created on auth.py .
"""
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
'''
error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422
    
"""
error handlers for 404.
"""
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
'''
 error handler for AuthError
'''
"""
error handlers for 401.
"""
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
"""
error handlers for 400.
"""
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
"""
error handlers for 403.
"""
@app.errorhandler(403)
def Forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "bad request"
    }), 403


