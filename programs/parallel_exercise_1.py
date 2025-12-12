from multiprocessing import Pool
import time
import os

def work(x):
    print(f"[Process {os.getpid()}] Starting task {x}")
    time.sleep(5)
    return f"Task {x} finished!"

def when_done(result):
    print(f" → Callback received: {result}")

if __name__ == "__main__":
    init = time.time()
    with Pool(4) as pool:
        for i in range(20):  
            pool.apply_async(work, args=(i,), callback=when_done)

        print("Main process is free to continue doing other things...")
        pool.close()
        pool.join()

    end = time.time()
    print(f"All tasks completed in {end - init} seconds")
