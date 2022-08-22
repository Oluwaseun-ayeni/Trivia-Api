import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:Password1!@localhost:5432/trivia_test'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_question(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_question"])
        self.assertTrue(len(data["questions"]))


    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000", json={"difficulty": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        res = self.client().delete("/questions/1")   
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["total_question"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)

    def test_404_if_queation_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")  
    
    def test_create_new_question(self):
        res = self.client().post("/question", json=self.new_question)
        data = json.loads(res.data)

        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['added_question'])
        self.assertTrue(data['questions'])
        

    def test_422_if_question_creation_fails(self):
        res = self.client().post("/books", json=self.new_question)
        data = json.loads(res.data)


        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")  

    
    def test_search_questions(self):
        res =self.client().post('/questions/search', json = {"searchTerm": "How"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])    
        
    

    def test_get_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)      

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])

    def test_get_quizzes_questions(self):
        res = self.client().post('/quizzes', json= {"previous_questions": [], 'quiz_category': {'type': 'Sports', 'id': 6}})
        data = json.loads(res.data)   

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(['question'])


  





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()