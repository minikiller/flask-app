import sys
import os
import time
import requests

from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

postpix = "_leela-zero"


class ImagesWatcher:
    def __init__(self, src_path):
        self.__src_path = src_path
        self.__event_handler = ImagesEventHandler()
        self.__event_observer = Observer()

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()

    def __schedule(self):
        self.__event_observer.schedule(
            self.__event_handler,
            self.__src_path,
            recursive=True
        )


class ImagesEventHandler(RegexMatchingEventHandler):
    IMAGES_REGEX = [r".*[^{postpix}]\.sgf$"]

    def __init__(self):
        super().__init__(self.IMAGES_REGEX)

    def on_created(self, event):
        self.process(event)

    def process(self, event):
        filename, ext = os.path.splitext(event.src_path)
        filename = f"{filename}{postpix}.sgf"
        kifu_id = filename.split("_")[1]
        print("kifu id is {}".format(kifu_id))
        url = 'https://localhost:5000/analyse/'+kifu_id
        with open(filename, "r") as f:
            data = f.read()
        d = {'analyse_data': data}
        r = requests.post(url, data=d)
        # extracting data in json format
        data = r.json()
        print(r.message)
        # print("i founde it {}".format(filename))


if __name__ == "__main__":
    # src_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    src_path = "/Users/sunlf/Documents/git-project/sgf-analyzer/"
    ImagesWatcher(src_path).run()
