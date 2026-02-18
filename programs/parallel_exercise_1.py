from multiprocessing import Pool
import time
import os

def print_numbers():
    for i in range(30):
        print("Alternative counter", i)
        time.sleep(1)

def work(x):
    print(f"[Process {os.getpid()}] Starting task {x}")
    time.sleep(5)
    return f"Task {x} finished!"

def send_notification(result):
    print(f" → Callback received: task {result} finished.")

if __name__ == "__main__":
    init = time.time()
    with Pool(4) as pool: 
        for i in range(20):  
            pool.apply_async(work, args=(i, ), callback=send_notification)

        pool.close()
        print("Main process is free to continue doing other things...")
        print_numbers() #example of other work while pool is working not related to pool
        pool.join()
        print("Pool completed.")
    

    end = time.time()
    print(f"All tasks completed in {end - init} seconds")
