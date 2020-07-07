""" from util.sgflib import  SGFParser, Node, Property

with open("2020-07-02.sgf", 'r', encoding="utf-8") as sgf_file:
    data = "".join([line for line in sgf_file])
    sgf_data = SGFParser(data).parse()

move_num = 0
cursor=sgf_data.cursor()
while not  cursor.atEnd:
    cursor.next()
    move_num += 1

print(move_num) """

from yaml import load
import util.settings as settings
with open(settings.PATH_TO_CONFIG) as yaml_stream:
    yaml_data = load(yaml_stream)

CONFIG = yaml_data['config']
print(CONFIG)