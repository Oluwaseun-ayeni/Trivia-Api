
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def paginate_question(request,questions):
    page = request.args.get('page', 1, type=int)
    start =(page -1) * QUESTIONS_PER_PAGE
    end = start * QUESTIONS_PER_PAGE

    all_questions = [question.format() for question in questions]
    current_question = all_questions[start:end]

    return current_question

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app,resources={r"/api/*":{"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route('/categories')
    def get_category():
        categories = Category.query.order_by(Question.category ==id).all()
        all_category = [category.format() for category in categories]
        if len(all_category) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': all_category,
            'total_category':len(Category.query.all())
            
        })   
    

    @app.route('/questions')
    def get_question():
        page = request.args.get("page", 1, type=int)
        questions= Question.query.order_by( Question.id).all()
        current_question = paginate_question(request,questions)

        categories = Category.query.all()
        all_categories = [category.format() for category in categories]
        category_dict = {}

        for category in all_categories:
            category_dict[category['id']] = category['type']

        if len(current_question) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'books': current_question,
            'total_questions':len(Question.query.all()),
            'page':page,
             
            
        })   

    
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            questions =Question.query.order_by(Question.id).all()
            current_books = paginate_question(request, questions)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "books": current_books,
                    "total_books": len(Question.query.all()),
                }
            )

        except:
            abort(422)    
    
   

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_dificulty = body.get("dificulty", None)

        try:
            question = Question(answer=new_answer, category=new_category, difficulty=new_dificulty)
            question.insert()

            questions = Question.query.order_by(Question.id).all()
            current_question = paginate_question(request, questions)

            return jsonify(
                {
                    "success": True,
                    "created": questions.id,
                    "question": current_question,
                    "total_question": len(Question.query.all()),
                }
            )

        except:
            abort(422)

   
    @app.route('/questions/search', methods=['POST'])
    def search_questions():

        search = request.get('search_term')
        questions = Question.query.filter(Question.name.ilike(f'%{search}%')).all()
        
        search_questions = [question.format() for question in questions]

        
        return jsonify(
                {
                    "success": True,
                    
                    "question": search_questions,
                    "total_question": len(Question.query.all()),
                }
            )
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_by_category(id):
        try:
                
            questions = Question.query.filter(Question.category == id).all()
            if questions == 0 or None:
                abort(404)

                
            else:
                current_questions = paginate_question(request, questions)
                
                categories = Category.query.filter(Category.id == id).all()
                category = [category.format() for category in categories]
                category_dict = {}
                for check in category:
                    category_dict[check['id']] = check['type']
                
                return jsonify({
                    "success":True,
                    "questions": current_questions,
                    "current_category": category_dict
                })        
        
        except:
            (422)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        
        try:
            body = request.get_json()

            current_category = body.get('quiz_category')
            previous_question = body.get('previous_questions')



            if current_category['type'] == 'click':
                gotten_questions = Question.query.filter(Question.id.notin_((previous_question))).all()

            else: 
                gotten_questions = Question.query.filter_by(category=current_category['id']
                ).filter(Question.id.notin_((previous_question))).all()

            questions = gotten_questions[random.randrange(0, len(gotten_questions))].format() if len(gotten_questions) > 0 else None

            return jsonify({
                "success": True,
                "question": questions
            })
        except:
            abort(422)        
      
       

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


    return app

