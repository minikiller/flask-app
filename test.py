def hello(**setting):
    setting.setdefault("name", "sunlf")
    setting.setdefault("first", "ssd")
    print(setting)


hello(name='123', data=1233)
