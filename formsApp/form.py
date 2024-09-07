from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class FormSearchProduct(FlaskForm):
    productName = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=30)], render_kw={"placeholder": "Ingrese el nombre del producto"})
    submit = SubmitField('Encontrar')
