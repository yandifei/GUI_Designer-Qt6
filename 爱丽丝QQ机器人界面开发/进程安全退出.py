from multiprocessing import Process
import atexit

processes = []
for _ in range(4):
    p = Process(target=child_function)
    p.start()
    processes.append(p)


def cleanup():
    for p in processes:
        p.terminate()

atexit.register(cleanup)