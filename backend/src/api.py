import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc

# from jose import jwt
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
"""
# db_drop_and_create_all()

# ROUTES
"""
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["GET"])
def get_drinks():
    # print(drinks)
    try:
        drinks = Drink.query.all()

        return jsonify({"success": True, "drinks": [drink.short() for drink in drinks]})
    except:
        abort(422)


"""
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_detail(token):
    try:
        drinks = Drink.query.all()
        return jsonify({"success": True, "drinks": [drink.long() for drink in drinks]})
    except:
        abort(404)


"""
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_drink(token):
    body = request.get_json()
    # print(body)
    title = body.get("title")
    recipe = body.get("recipe")
    # print(recipe, title)
    try:
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        """ converted Json object to string so it can be entered into the database """
        new_drink.insert()
        return jsonify({"success": True, "drinks": [new_drink.long()]})
    except:
        abort(422)


"""
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def edit_drink(token, id):
    drink = Drink.query.get(id)
    # Respond with 404 if Drink  not found
    if drink:
        body = request.get_json()
        title = body.get("title")
        recipe = body.get("recipe")

        if title != drink.title:
            drink.title = title
        if recipe != drink.recipe:
            drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify({"success": True, "drinks": [drink.long()]})
    else:
        abort(404)


"""
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(token, id):
    drink = Drink.query.get(id)
    if drink:
        try:
            drink.delete()
            return jsonify({"success": True, "delete": drink.id})
        except:
            abort(422)
    else:
        abort(404)


# Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


"""
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

"""
"""
@TODO implement error handler for 404
    error handler should conform to general task above
"""


@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not Found"}), 404


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above
"""


@app.errorhandler(AuthError)
def auth_error(error):
    return (
        jsonify(
            {
                "success": False,
                "error": error.status_code,
                "message": "Unauthorized Access",
            }
        ),
        401,
    )


if __name__ == "__main__":
    app.debug = True
    app.run()
