import os
from flask import (
    Flask,
    request,
    jsonify,
    abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from database.models import (
    db_drop_and_create_all,
    setup_db,
    Movie,
    Actor
)
from auth.auth import AuthError, requires_auth


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object('config')  # Import things from config
    setup_db(app)
    CORS(app)

    '''
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    '''
    db_drop_and_create_all()

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    # ROUTES
    '''
    Implement endpoint
        /
            it should be a public endpoint
        returns status code 200 and json
            {"success": True, "message": "hello world"}
            or appropriate status code indicating reason for failure
        It is always good to show something at the root route
        to show that the API is working!
    '''

    @app.route('/')
    def home():
        return jsonify({
            'success': True,
            'message': 'hello world'
        })

    '''
    Implement endpoint
        GET /actors
            it should require the 'get:actors' permission
        returns status code 200 and json {"success": True, "actors": actors}
            where actors is the list of actors
            or appropriate status code indicating reason for failure
    '''
    @app.route('/actors')
    # require the 'get:actors' permission
    @requires_auth(permission="get:actors")
    def get_actors(payload):
        data = Actor.query.all()
        actors = list(map(Actor.get_actor, data))
        if actors is None or len(actors) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'actors': actors
        })

    '''
    Implement endpoint
        GET /movies
            it should require the 'get:movies' permission
        returns status code 200 and json {"success": True, "movies": movies}
            where movies is the list of movies
            or appropriate status code indicating reason for failure
    '''
    @app.route('/movies')
    @requires_auth('get:movies')
    def get_movies(payload):
        data = Movie.query.all()
        movies = list(map(Movie.get_movie, data))
        if movies is None or len(movies) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'movies': movies
        })

    '''
    Implement endpoint
        POST /actors
            it should create a new row in the actors table
            it should require the 'post:actors' permission
            it should contain the actor.get_actor data representation
        returns status code 200 and json {"success": True, "actors": actor}
            where actor an array containing only the newly created actor
            or appropriate status code indicating reason for failure
    '''
    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def post_actor(payload):
        body = request.get_json()
        if body is None:
            abort(404)
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')
        # verify id there is no duplicate
        duplicate = Actor.query.filter(Actor.name == name).one_or_none()
        if duplicate is not None:
            abort(400)
        try:
            new_actor = Actor(name=name, age=age, gender=gender)
            new_actor.insert()
            return jsonify({
                'success': True,
                'actors': [new_actor.get_actor()]
            })
        except Exception as error:
            abort(422)

    '''
    Implement endpoint
        POST /movies
            it should create a new row in the movies table
            it should require the 'post:movies' permission
            it should contain the movie.get_movie data representation
        returns status code 200 and json {"success": True, "movies": movie}
            where movie an array containing only the newly created movie
            or appropriate status code indicating reason for failure
    '''
    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def post_movie(payload):
        body = request.get_json()
        if 'title' not in body:
            abort(404)
        title = body.get('title')
        release_date = body.get('release_date')
        # verify id there is no duplicate
        duplicate = Movie.query.filter(Movie.title == title).one_or_none()
        if duplicate is not None:
            abort(400)
        try:
            new_movie = Movie(title=title, release_date=release_date)
            new_movie.insert()
            return jsonify({
                'success': True,
                'movies': [new_movie.get_movie()]
            })
        except Exception as error:
            abort(422)

    '''
    Implement endpoint
        PATCH /actors/<actor id>
            it should update an existing row in the actors table
            it should require the 'patch:actors' permission
            it should contain the actor.get_actor data representation
        returns status code 200 and json {"success": True, "actors": actor}
            where actor an array containing only the updated actor
            or appropriate status code indicating reason for failure
    '''
    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(payload, actor_id):
        # get the element with given id
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if actor is None:
            abort(404)
        body = request.get_json()  # get the body
        if body is None:
            abort(404)

        updated_name = body.get('name')
        updated_age = body.get('age')
        updated_gender = body.get('gender')

        if updated_name is not None:
            actor.name = updated_name
        if updated_age is not None:
            actor.age = updated_age
        if updated_gender is not None:
            actor.gender = updated_gender

        try:
            actor.update()  # update the record
            return jsonify({
                'success': True,
                'actors': [actor.get_actor()]
            })
        except Exception as error:
            abort(422)

    '''
    PATCH /movies/<movie id>
        it should update an existing row in the movies table
        it should require the 'patch:movies' permission
        it should contain the movie.get_movie data representation
    returns status code 200 and json {"success": True, "movies": movie}
        where movie an array containing only the updated movie
        or appropriate status code indicating reason for failure
    '''
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(payload, movie_id):
        # get the element with given id
        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if movie is None:
            abort(404)
        body = request.get_json()  # get the body
        if body is None:
            abort(404)

        updated_title = body.get('title')
        updated_release_date = body.get('release_date')

        if updated_title is not None:
            movie.title = updated_title
        if updated_release_date is not None:
            movie.release_date = updated_release_date

        try:
            movie.update()  # update the record
            return jsonify({
                'success': True,
                'movies': [movie.get_movie()]
            })
        except Exception as error:
            abort(422)

    '''
    DELETE /actors/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:actors' permission
    returns status code 200 and json {"success": True, "deleted": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
    '''
    @app.route('/actors/<actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        # get the actor to delete
        selected_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if selected_actor is None:
            abort(404)
        try:
            selected_actor.delete()  # delete the item
            return jsonify({
                "success": True,
                "deleted": actor_id
            })
        except Exception as error:
            abort(422)

    '''
    DELETE /movies/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:movies' permission
    returns status code 200 and json {"success": True, "deleted": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
    '''
    @app.route('/movies/<movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
        # get the movie to delete
        selected_movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if selected_movie is None:
            abort(404)
        try:
            selected_movie.delete()  # delete the item
            return jsonify({
                "success": True,
                "deleted": movie_id
            })
        except Exception as error:
            abort(422)

    # Error Handling
    '''
    Implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                jsonify({
                        "success": False,
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    '''

    '''
    Implement error handler for 404
        error handler should conform to general task above
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    '''
    Implement error handler for 400
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    '''
    Implement error handler for 405
    '''
    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    '''
    Implement error handler for 422
    '''
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    '''
    Implement error handler for AuthError
        error handler should conform to general task above
    '''
    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "code": error.error['code'],
            "message": error.error['description']
        }), error.status_code

    return app


APP = create_app()

if __name__ == '__main__':
    # APP.run(host='0.0.0.0', port=8080, debug=False)
    APP.run()
