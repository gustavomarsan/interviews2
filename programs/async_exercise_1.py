import asyncio
import time
from datetime import datetime

async def task_example(name):
    print(f"Task {name}: Starting")
    await asyncio.sleep(5)  # simulate 5 seconds delay
    print(f"Task {name}: Completed after {2} seconds")
    return "Finish time " + datetime.now().strftime("%H:%M:%S")+ f".{datetime.now().microsecond:06d}"


async def main():
    init = time.time()

    #create tasks with 5 seconds delay each one
    tasks = [task_example(i) for i in range(10)]

    results = await asyncio.gather(*tasks)
    print("All task results:", results)

   

asyncio.run(main())