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


class QuizForm(FlaskForm):
    quiz_title = StringField(
        "Quiz Title",
        validators=[DataRequired()],
        render_kw={"placeholder": "Type your quiz title"},
    )
    question_type = SelectField(
        "Type: ",
        choices=["Question Type", "Multiple Choice", "none"],
        validators=[DataRequired()],
    )
    num_answer_field = SelectField(
        "Number of answer fields",
        choices=[3, 4],
        validators=[DataRequired()],
        id="num_field",
    )
    submit = SubmitField("Go", id="submit")
    # q_numbers = IntegerField("Number of questions", render_kw={"placeholder": "0"}, validators=[DataRequired()])
    # score_for_each = IntegerField("Score for each correct answer", render_kw={"placeholder": "0"}, validators=[DataRequired()])


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class QuestionForm(FlaskForm):
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
