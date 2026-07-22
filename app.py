import os
import json
import random
import logging
import sys
from flask import Flask, render_template, request, redirect, url_for, session

application = Flask(__name__)

# Helper function to dynamically load JSON based on subcategory name
DATA_DIR = os.path.join(application.root_path, 'data')

def load_subcategory_data(sub_category):
    """Loads a specific JSON file corresponding to sub_category."""
    file_path = os.path.join(DATA_DIR, f"{sub_category}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/quizShowCase', methods=['GET', 'POST'])
def quizShowCase():
    category = request.args.get('category', '')
    subCategory = request.args.get('subCategory', '')
    return render_template('quizShowCase.html', value=category, subCategory=subCategory)


@application.route('/questions', methods=['GET', 'POST'])
def questions():
    if request.method == 'GET':
        category = request.args.get('category')
        subCategory = request.args.get('subCategory')
        quiz = request.args.get('quiz')
        
        sub_data = load_subcategory_data(subCategory) if subCategory else None

        if sub_data and subCategory in sub_data and quiz in sub_data[subCategory]:
            quiz_questions = sub_data[subCategory][quiz]
            picture = []
            
            # Build a separate dictionary for the template so we don't mutate the original data
            display_questions = {}

            for q_num, q_data in quiz_questions.items():
                if "picture" in q_data:
                    picture.append([q_num, q_data["picture"]])
                
                # Copy the question data
                q_copy = q_data.copy()
                
                # Convert choices into a list of tuples: [("1", "Ans A"), ("2", "Ans B"), ...]
                items = list(q_data["multipleChoiceAnswers"].items())
                random.shuffle(items)  # Shuffle the choices safely
                
                # Assign shuffled choices to our copy
                q_copy["shuffled_answers"] = items
                display_questions[q_num] = q_copy

            return render_template('questions.html',
                                   category=category,
                                   subCategory=subCategory,
                                   quiz=quiz,
                                   questions=display_questions,
                                   picture=picture)
        else:
            return render_template('index.html', error="Invalid quiz or subcategory missing")
    else:
        return render_template('questions.html', value='Questions Page')


@application.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        category = request.form.get('category')
        subCategory = request.form.get('subCategory')
        quiz = request.form.get('quiz')
        
        sub_data = load_subcategory_data(subCategory) if subCategory else None
        
        if not sub_data or subCategory not in sub_data or quiz not in sub_data[subCategory]:
            return redirect(url_for('index'))

        quiz_questions = sub_data[subCategory][quiz]
        score = 0
        total = len(quiz_questions)
        
        for q_num, q_data in quiz_questions.items():
            submitted_answer = request.form.get(f'q{q_num}')
            
            # Compare the submitted string directly with correctAnswer
            if submitted_answer and submitted_answer.strip() == q_data['correctAnswer'].strip():
                score += 1
        
        return render_template('results.html',
                               category=category,
                               subCategory=subCategory,
                               quiz=quiz,
                               score=score,
                               total=total,
                               submitted=True)
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    application.run(debug=True)