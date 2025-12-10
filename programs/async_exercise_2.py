import asyncio
import time
from datetime import datetime

async def task_example(name, delay_seconds):
    print(f"Task {name}: Starting")
    await asyncio.sleep(delay_seconds)
    print(f"Task {name}: Completed!")
    return name, datetime.now().strftime("%H:%M:%S.%f")

async def main():
    init = time.time()

    tasks = [task_example(f"task_{i}", 5) for i in range(10)]

    for coro in asyncio.as_completed(tasks):
        name, finish_time = await coro  # Wait for completion
        print(f"➡️ {name} finished at {finish_time}")

    end = time.time()
    print(f"\nAll tasks completed in {end - init:.2f} seconds")

asyncio.run(main())
