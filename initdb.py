# -- coding:UTF-8 --
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import api
from model import db
import model
import datetime

avatar = "http://sunlingfeng.0431zy.com/1.png"

db.drop_all()
db.create_all()

hashed_password = generate_password_hash('1', method='sha256')
testuser_password = generate_password_hash('bibi', method='sha256')
user1 = model.User(
    public_id="68b5c1c1-86ab-47b2-82ac-5ce76f2d218a",
    name='admin',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=True,
    avatar=avatar
)
user2 = model.User(
    public_id="234a1099-de35-48ea-9e64-0474c6b4dcfc",
    name='sunhy1',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False,
    avatar=avatar
)
user3 = model.User(
    public_id="bd0e1ff3-36b6-49ea-a594-439768849f5b",
    name='sunhy2',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False,
    avatar=avatar
)
user4 = model.User(
    public_id="14c48dc4-30f0-406a-8de5-7d4b8e6d4730",
    name='sunlf1',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False,
    avatar=avatar
)
user5 = model.User(
    public_id="6fd9722b-d3e5-465d-b11a-14d2c4ada4a6",
    name='sunlf2',
    password=hashed_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False,
    avatar=avatar
)

user6 = model.User(
    public_id="1925dbf8-1889-415a-8101-cf340a83f64f",
    name='laomian',
    password=testuser_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False,
    avatar=avatar
)

user7 = model.User(
    public_id="cd78473c-3d2d-4fa8-87aa-236977e9c656",
    name='sanda',
    password=testuser_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False,
    avatar=avatar
)
user8 = model.User(
    public_id="b2bf42c2-42bb-46d9-be48-cf9cf1b7c358",
    name='linlin',
    password=testuser_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False,
    avatar=avatar
)

user9 = model.User(
    public_id="b2bf42c2-42bb-46d9-be48-cf9cf1b7c359",
    name='cheng',
    password=testuser_password,
    email='95006410@qq.com',
    mobile='13601072289',
    isadmin=False,
    avatar=avatar
)

start_date = datetime.datetime.strptime(
    "2020-10-22 22:23:00", "%Y-%m-%d %H:%M:%S")
now_time = datetime.datetime.now()
game1 = model.Game(
    name="对局一",
    comment="ka rer",
    blackone_id="sunlf1",
    blacktwo_id="sunlf2",
    whiteone_id="sunhy1",
    whitetwo_id="sunhy2",
    start_time=start_date,
    total_time=6000,
    create_date=now_time,
    user_id=1,
    public=True,
    password=None,
    status='未开始',
)

game2 = model.Game(
    name="对局二",
    comment="ka rer",
    blackone_id="sunhy1",
    blacktwo_id="sunlf1",
    whiteone_id="cheng",
    whitetwo_id="laomian",
    start_time=start_date,
    create_date=now_time,
    total_time=6000,
    public=True,
    password=None,
    status='未开始',
    user_id=1
)

db.session.add(user1)
db.session.add(user2)
db.session.add(user3)
db.session.add(user4)
db.session.add(user5)
db.session.add(user6)
db.session.add(user7)
db.session.add(user8)
db.session.add(user9)
db.session.add(game1)
db.session.add(game2)

db.session.commit()
