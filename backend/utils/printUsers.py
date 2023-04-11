from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta

def printUsers(User:DefaultMeta):
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'email': user.email,
            'password': user.password,
            'docsources': [docsource.to_dict() for docsource in user.docsources]
        }
        user_list.append(user_data)
    print(user_list)