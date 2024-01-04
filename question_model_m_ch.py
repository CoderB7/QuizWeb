from forms import QuizForm


class QuestionMCh:
    def __init__(self, q_text, c_answer, q_point, answers):
        self.question_text = q_text
        self.correct_answer = c_answer
        self.question_point = q_point
        self.answers = answers

    def mch_form(self):
        form = QuizForm()

        pass

