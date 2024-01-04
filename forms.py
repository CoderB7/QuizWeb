from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    SelectField,
    IntegerField,
    RadioField,
    FieldList,
)
from wtforms.validators import DataRequired, URL, InputRequired
from wtforms import widgets, SelectMultipleField
from wtforms.widgets import Input


class CustomTextInput(Input):
    def __call__(self, field, **kwargs):
        custom_id = kwargs.pop("id", field.id)
        return super(CustomTextInput, self).__call__(field, id=custom_id, **kwargs)


class RegisterForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired()],
        render_kw={"placeholder": "e.g.john@your-domain.com"},
    )
    education = SelectField(
        "Education:  ",
        choices=["Choose...", "Teacher", "Student"],
        validators=[DataRequired(), InputRequired()],
    )
    first_name = StringField(
        "First name",
        validators=[DataRequired()],
        render_kw={"placeholder": "e.g. John"},
    )
    second_name = StringField(
        "Second name",
        validators=[DataRequired()],
        render_kw={"placeholder": "e.g. Smith"},
    )
    phone_number = StringField(
        "Phone number",
        validators=[DataRequired()],
        render_kw={"placeholder": "+00 000 000 000"},
    )
    password = StringField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Your Password"},
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired()],
        render_kw={"placeholder": "your-email@gmail.com"},
    )
    password = StringField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Your Password"},
    )
    submit = SubmitField("Log In")


class TrueFalseForm(FlaskForm):
    quiz_title = StringField(
        "Quiz Title",
        validators=[DataRequired()],
        render_kw={"placeholder": "Type your quiz title"},
    )


class MultipleChoiceForm(FlaskForm):
    quiz_title = StringField(
        "Quiz Title",
        validators=[DataRequired()],
        render_kw={"placeholder": "Type your quiz title"},
    )
    num_answer_field = SelectField(
        "Number of answer fields",
        choices=[3, 4],
        validators=[DataRequired()],
        id="num_field",
    )
    # q_numbers = IntegerField("Number of questions", render_kw={"placeholder": "0"}, validators=[DataRequired()])
    # score_for_each = IntegerField("Score for each correct answer", render_kw={"placeholder": "0"}, validators=[DataRequired()])


class OpenTriviaForm(FlaskForm):
    question_amount = IntegerField(
        "Number of Questions:",
        validators=[InputRequired(), DataRequired()],
        render_kw={"placeholder": 10},
    )
    category = SelectField(
        "Select Category:",
        choices=[("", "Any Category"), (9, "General Knowledge"), (10, "Entertainment: Books"), (11, "Entertainment: Film"),
                 (12, "Entertainment: Music"), (13, "Entertainment: Musicals & Theatres"),
                 (14, "Entertainment: Television"), (15, "Entertainment: Video Games"),
                 (16, "Entertainment: Board Games"), (17, "Science & Nature"),
                 (18, "Science: Computers"), (19, "Science: Mathematics"), (20, "Mythology"), (21, "Sports"),
                 (22, "Geography"), (23, "History"), (24, "Politics"),
                 (25, "Art"), (26, "Celebrities"), (27, "Animals"), (28, "Vehicles"), (29, "Entertainment: Comics"),
                 (30, "Science: Gadgets"),
                 (31, "Entertainment: Japanese Anime & Manga"), (32, "Entertainment: Cartoon & Animations")
                 ],
        validate_choice=True
    )
    difficulty = SelectField(
        "Select Difficulty:",
        choices=[("", "Any Difficulty"), ("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        validate_choice=True
    )
    type = SelectField(
        "Select Type:",
        choices=[("", "Any Type"), ("multiple", "Multiple Choice"), ("boolean", "True / False")],
        validate_choice=True
    )
    point = IntegerField(
        label="Set Score",
        validators=[InputRequired(), DataRequired()],
        render_kw={"placeholder": 1},
    )


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class QuestionFormTF(FlaskForm):
    question = StringField(
        label="", validators=[DataRequired()], render_kw={"placeholder": "Question"}
    )
    correct_answer = StringField(
        label="Correct answer here",
        validators=[DataRequired()],
        render_kw={"placeholder": "Correct answer"},
    )
    point = IntegerField(
        label="Set Score",
        validators=[InputRequired(), DataRequired()],
        render_kw={"placeholder": 1},
    )
    true_false = RadioField(
        label="",
        choices=[("True", "True"), ("False", "False")],
        validators=[DataRequired()],
        coerce=bool,
    )


class QuestionFormMCh(FlaskForm):
    dynamic_answers = FieldList(
        StringField(
            label="", validators=[InputRequired()], render_kw={"placeholder": "Answer"}
        ),
        min_entries=0,
        widget=CustomTextInput(),
    )
    question = StringField(
        label="", validators=[InputRequired()], render_kw={"placeholder": "Question"}
    )
    correct_answer = StringField(
        label="Correct answer here",
        validators=[InputRequired()],
        render_kw={"placeholder": "Correct Answer"},
    )
    answer_1 = StringField(
        label="", validators=[InputRequired()], render_kw={"placeholder": "Answer"}
    )
    point = IntegerField(
        label="Set score",
        validators=[InputRequired(), DataRequired()],
        render_kw={"placeholder": 1},
    )


class AnswerForm(FlaskForm):
    answer_n = StringField(
        label="", validators=[DataRequired()], render_kw={"placeholder": "Answer"}
    )
