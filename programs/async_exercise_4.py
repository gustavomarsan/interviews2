#this example shows how manage:
#  *100 async tasks
#  *catch error inside the callback
#  *Access the result inside the callback


import asyncio
import random
import time

# ---------------------------
# WORKER: async function
# ---------------------------
async def do_work(i):
    await asyncio.sleep(random.uniform(0.1, 0.3))

    # randomly raise an error to test error handling
    if random.random() < 0.1:  # 10% chance of failure
        raise ValueError(f"Task {i} failed!")

    return f"Result of task {i}"


# ---------------------------
# CALLBACK: runs when task finishes
# ---------------------------
def on_done(task: asyncio.Task):
    try:
        result = task.result()   # <-- This will raise if task failed
        print(f"[CALLBACK] Success → {result}")

    except Exception as e:
        print(f"[CALLBACK] ERROR *********** {e}")

async def main():
    tasks = []

    for i in range(10):
        t = asyncio.create_task(do_work(i))
        t.add_done_callback(on_done)
        tasks.append(t)
    
    # wait for all tasks to finish
    await asyncio.gather(*tasks, return_exceptions=True)


asyncio.run(main())
