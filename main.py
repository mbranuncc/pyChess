from threading import Thread
import subprocess
import time

if __name__ == "__main__":
    t1 = Thread(target=subprocess.run, args=(["python3", "app.py"],))
    t2 = Thread(target=subprocess.run, args=(["python3", "visuals.py"],))

    t1.start()
    time.sleep( 5 )
    t2.start()

    t1.join()
    t2.join()