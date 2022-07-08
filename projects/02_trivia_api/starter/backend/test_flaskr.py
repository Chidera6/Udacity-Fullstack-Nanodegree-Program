import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    #"""This class represents the trivia test case"""
    def setUp(self):
        #"""Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:chidera@localhost:5432/trivia_test'
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question":"Who is the first female vice president of USA","answer":"Kamala Harris","category":"6","difficulty":"7"}
        
    
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
     
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/categories?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
       

    def test_retrieve_question(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    

    def test_delete_questions(self):
        res = self.client().delete("/questions/20")
        data = json.loads(res.data)
        question = Question.query.filter_by(id==id).all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        

    def test_post_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_if_question_post_fails(self):
        res = self.client().post("/books", json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        
        
    def test_search_question(self):
        res = self.client().post("/search",json={"search":"what"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        

    def test_question_search_fails(self):
        res = self.client().post("questions/search",json={"search":''})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        


    def test_get_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        

    def test_get_by_category_not_found(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_quiz_question(self):
        res = self.client().post("/quizzes", json={ 
            "previous_questions": [],'quiz_category': {
                'type': 'Entertainment',
                'id': '3'
            }})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        

    def test_quiz_not_found_category(self):
        res = self.client().post('/quizzes', json={
            "previous_questions": [6],
            "quiz_category": {
                "type": "vision science",
                "id": "5000"
            }
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()