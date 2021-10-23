import threading
from time import sleep


def do_this(what):
    whoami(what)


def whoami(what):
    print("Thread  says: %s" % what)
    sleep(1)


if __name__ == "__main__":
    for n in range(4):
        whoami("I'm the main program")
        p = threading.Thread(target=do_this, args=("I'm function %s" % n,))
        p.start()
