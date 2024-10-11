from flask import Flask
from application.config import Config
from application.models import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        
        # Add Admin into the DB
        if not Users.query.filter_by(username = 'admin').first():
            admin_user = Users(username = 'admin', password = 'admin', usertype = 'admin')
            db.session.add(admin_user)
        
        db.session.commit()
    
    return app

app = create_app()

from application.render import *

if __name__ == '__main__':
    app.run(port = 5500, debug = True)