from api import db
import api
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db.drop_all()
db.create_all()

hashed_password = generate_password_hash('123456', method='sha256')

user1 = api.User(
    public_id=str(uuid.uuid4()),
    name='admin',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=True
)
user2 = api.User(
    public_id=str(uuid.uuid4()),
    name='sunhy1',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False
)
user3 = api.User(
    public_id=str(uuid.uuid4()),
    name='sunhy2',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False
)
user4 = api.User(
    public_id=str(uuid.uuid4()),
    name='sunlf1',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False
)
user5 = api.User(
    public_id=str(uuid.uuid4()),
    name='sunlf1',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False
)

db.session.add(user1)
db.session.add(user2)
db.session.add(user3)
db.session.add(user4)
db.session.add(user5)

db.session.commit()
