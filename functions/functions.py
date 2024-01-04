import statistics
import random
import requests


def shuffle_answers(correct_answer, wrong_answers, q_type):
    answer_bank = []
    if q_type == 'multiple':
        answer_bank = [correct_answer, wrong_answers[0], wrong_answers[1], wrong_answers[2]]
    elif q_type == 'boolean':
        answer_bank = [correct_answer, wrong_answers[0]]
    random.shuffle(answer_bank)
    return answer_bank


def trivia_request(q_amount, category, difficulty, q_type):

    parameters = {
        "amount": q_amount,
        "category": category,
        "difficulty": difficulty,
        "type": q_type,
    }
    print(parameters)
    response = requests.get("https://opentdb.com/api.php", params=parameters)
    response.raise_for_status()
    data = response.json()
    print(data)
    question_data = data["results"]
    return question_data


def score_calculator(student_answers, question_data, from_library, point):
    score = 0
    total_score = 0

    if from_library:
        print(student_answers)
        question_amount = len(question_data)
        for n in range(0, question_amount):
            if question_data[n]["correct_answer"] == student_answers[f"Q{n+1}"][0]["answer"]:
                score += point
            total_score += point
    else:
        for key in question_data:
            if question_data[key]["correct_answer"] == student_answers[key][0]["answer"]:
                score += int(question_data[key]["point"])
            total_score += int(question_data[key]["point"])
    score_data = [score, total_score]
    return score_data


def total_score_(question_data):
    total_point = 0
    for key in question_data:
        total_point += int(question_data[key]["point"])
    return total_point


def find_max_point(points):
    max_n = max(points)
    return max_n


def find_min_point(points):
    min_n = min(points)
    return min_n


def find_average_point(points):
    average_n = statistics.mean(points)
    return average_n
