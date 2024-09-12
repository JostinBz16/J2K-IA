from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class FormSearchProduct(FlaskForm):
    productName = TextAreaField('Nombre', validators=[DataRequired(), Length(min=3)], render_kw={"placeholder": "Ingrese el nombre del producto"})
    submit = SubmitField('Encontrar')
