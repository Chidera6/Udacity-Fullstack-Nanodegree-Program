import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
  page = request.args.get("page", 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app,resources={r"/api/*": {"origins": "*"}})
 
  @app.after_request
  def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
 
  @app.route("/categories")
  def retrieve_categories():
    selection = Category.query.order_by(Category.id).all()
    current_category = paginate_questions(request,selection)
    if len(current_category) == 0:
      abort(404)
      return jsonify ({
      "categories" : {cat.id: cat.type for cat in user_to_get}
      })

  
  @app.route("/questions?page=${integer}")
  def retrieve_question():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    user_to_get = Category.query.order_by(Category.id).all()
    #current_category = paginate_questions(request,user_to_get)
    if len(current_questions) == 0:
      abort(404)
    return jsonify({
      "success": True,
      "questions": current_questions,
      "total_questions": len(Question.query.all()),
      "categories" : {cat.id: cat.type for cat in user_to_get},
      })


  @app.route("/questions/<int:id>",methods=["DELETE"])
  def delete_question(id):
    try:
        selection = Question.query.filter_by(id=id).one_or_none()
        if selection is None:
          abort(404)
        else:
          selection.delete()
        return jsonify({
          "success": True,
        
          })
    except Exception:
      abort(422)
  
  @app.route("/questions",methods=['POST'])
  def post_question():
    body = request.get_json()

    new_question = body.get("question",None)
    new_answer = body.get("answer",None)
    new_category = body.get("category",None)
    new_difficulty = body.get("difficulty",None)
    try:
      question = Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
      question.insert()
      return jsonify({
        "success" : True,
      })
    except Exception:
      abort(422)

  
  @app.route("/search",methods=['POST'])
  def search_question():
    body = request.get_json()
    search = body.get('searchTerm',None)
  
    selection = Question.query.order_by(Question.id).filter(Question.question.ilike(f'%{search}%'))
    current_question = paginate_questions(request,selection)
    return jsonify(
      {
        "success": True,
        "questions": current_question,
        "total_questions": len(Question.query.all())


      }
    )

  
  @app.route("/categories/<int:id>/questions")
  def get_by_category(id):
    if selection := Category.query.filter_by(id=id).one_or_none():
      x = Question.query.filter_by(category=str(id)).all()
      current_questions = paginate_questions(request,x)
      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(Question.query.all()),
        "current_category_string": selection.type,
       })
    else:
      abort(404)

  @app.route("/quizzes",methods=['POST'])
  def quiz_question():
    try:
      body = request.get_json()
      previous_questions = body.get('previous_questions', None)
      new_category = body.get('new_category', None)
      category_id = new_category['id']
      if category_id == 0:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions),
        Question.category == category_id).all()
        question = None
        if(questions):
          question = random.choice(questions)
          return jsonify({
                'success': True,
                'question': question.format()
            })

    except Exception:
            abort(422)

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def not_found(error):
    return (jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"}),
            404,)

  @app.errorhandler(422)
  def unprocessable(error):
    return (jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"}),
            422,
        )
  @app.errorhandler(400)
  def bad_request(error):
    return (jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }),
    400)

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "internal server error"
      }), 500

  return app
