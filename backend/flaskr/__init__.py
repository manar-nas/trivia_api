import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json
from sqlalchemy import func
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
   '''

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    # Pagination to handling large collections of data.

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions

    # handle GET requests for all available categories.
    @app.route('/categories')
    def retrieve_categories():
        category_query = Category.query.order_by(Category.id).all()
        count = 1
        categories = {}
        for category in category_query:
            if len(categories) != 0:
                categories.update({str(count): category.type})
            else:
                categories = {
                    str(count): category.type
                }
            count += 1

        return jsonify({
            'success': True,
            'categories': categories
        })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

    @app.route('/questions')
    def retrieve_questions():
        # Get all questions and paginate
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        # abort 404 if no questions
        if len(current_questions) == 0:
            abort(404)
        # Get all categories
        category_query = Category.query.order_by(Category.id).all()
        count = 1
        categories = {}
        for category in category_query:
            if len(categories) != 0:
                categories.update({str(count): category.type})
            else:
                categories = {
                    str(count): category.type
                }
            count += 1
       # Return data
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': categories,
        })
    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # Get a question by id
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            # abort 404 if there is no question found
            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            # Return data results
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        # abort unprocessable if exception
        except Exception:
            abort(422)

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions', methods=['POST'])
    def retrieve_questions_based_on_searchTerm():
        body = request.get_json()
        try:
            if (body.get('searchTerm', None)):
                search = body.get('searchTerm', None)
                # select all questions from Question table based on search term
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike(f'%{search}%')).all()
                current_questions = paginate_questions(request, selection)
                # Return data results
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
            # Create a new question if no search
            else:
                new_question = body.get('question', None)
                new_answer = body.get('answer', None)
                new_difficulty = body.get('difficulty', None)
                new_category = body.get('category', None)
                # Create a new question
                question = Question(question=new_question, answer=new_answer,
                                    category=new_category, difficulty=new_difficulty)
                # Insert a new question
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                # Return data results
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

        except Exception:
            abort(422)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_based_on_category(category_id):
        # Get a category by id and compare it with Question.category after converting it to string
        selection = Question.query.filter(Question.category == str(
            category_id)).order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        # abort 404 if category is not found
        if len(current_questions) == 0:
            abort(404)
        current_Category_query = Category.query.with_entities(
            Category.type).filter(Category.id == category_id).one_or_none()
        # Return data results
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_Category': current_Category_query.type
        })

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.   
   '''

    @app.route('/quizzes', methods=['POST'])
    def retrieve_question_to_play():
        body = request.get_json()
        category = body.get('quiz_category')
        previousQuestions = body.get('previous_questions')
        total_questions = Question.query.filter(
            Question.category == category['id']).all()
        # abort 400 if there are not category or previous questions found
        if category is None:
            abort(400)
        if previousQuestions is None:
            abort(400)
        # select question from Question table not in previousQuestions with random
        questions = Question.query.filter(~Question.id.in_(
            previousQuestions)).order_by(func.random())
        if category['id'] != 0:
            # select question based on category
            questions = questions.filter(Question.category == category['id'])
            # if the length of previous questions equal total questions return without question
            if len(previousQuestions) == len(total_questions):
                return jsonify({
                    'success': True
                })
        # Return data
        return jsonify({
            'success': True,
            'question': questions.first().format()
        })

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    # error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(422)
    def unprocrssable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocrssable"
        }), 422

    @app.errorhandler(500)
    def internal_Server_rror(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "METHOD NOT ALLOWED"
        }), 405

    return app
