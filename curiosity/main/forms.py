from wtforms import StringField
from wtforms.validators import DataRequired

class SearchForm():
    search = StringField('search', [DataRequired()])
    submit = SubmitField('Search',
                       render_kw={'class': 'btn btn-success btn-block'})

