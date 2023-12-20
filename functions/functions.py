import statistics


def score_calculator(student_answers, question_data):
    score = 0
    total_score = 0
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
