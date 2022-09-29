import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin
import ast

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# CORS(app, resources={"/": {"origins": "*"}})
# CORS Headers
""" @app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,PATCH,POST,DELETE,OPTIONS"
    )
    response.headers.add(
        "Access-Control-Allow-Origin", "http://127.0.0.1:4200"
    )
    
    return response
 """
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
# @requires_auth('get:drinks')
# def drinks(jwt):

def drinks():
    selection = Drink.query.all()
    if len(selection) == 0:
        abort(404)
        
    drinks = [drink.short() for drink in selection]
    
    return jsonify(
        {
            "success": True,
            "drinks": drinks,
        }
    ),200
    
    

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')

def drinks_detail(jwt):
    selection = Drink.query.all()
    if len(selection) == 0:
        abort(404)
        
    drinks = [drink.long() for drink in selection]
    
    return jsonify(
        {
            "success": True,
            "drinks": drinks,
        }
    ),200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')

def post_drinks(jwt):
    body = request.get_json()
    title = body.get('title','')
    recipe = body.get('recipe','')
    drink = Drink(
        title=title,
        # recipe=json.loads(recipe)
        recipe=str(recipe).replace("'", "\"")
    )
    try:
        drink.insert()
        
    except:
        abort(422)
    
    return jsonify(
        {
            "success": True,
            "drinks": drink.long(),
        }
    ),200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')

def drinks_patch(jwt,id):
    body = request.get_json()
    
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)

        if 'title' in body:
            drink.title = body.get("title")

        if 'recipe' in body:
            drink.recipe = str(body.get("recipe")).replace("'", "\"") 

        drink.update()
        

    except:
        abort(400)
        
    return jsonify(
        {
            "success": True,
            "drinks": list(Drink.query.get(id).long()),
        }
    ),200
    


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')

def drinks_delete(jwt,id):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)

        drink.delete()
        
    except:
        abort(422)
    
    return jsonify(
        {
            "success": True,
            "delete": id,
        }
    ), 200
# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


#Methode not allowed
@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
    "success": False, 
    "error": 405,
    "message": "method not allowed"
    }), 405

    
#Bad request
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
    "success": False, 
    "error": 400,
    "message": "bad request"
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''  

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
