
import asyncio
import time

async def eating():
    print("I'm starting to eat")
    await asyncio.sleep(5)
    print("I finished eating")

async def drinking_lemonade():
    print("I'm starting to drink")
    await asyncio.sleep(8)
    print("I finished drinking")
    # Start drinking coffee when lemonade finishes
    asyncio.create_task(drinking_coffee())

async def washing_clothes():
    print("I'm starting to wash clothes")
    await asyncio.sleep(20)
    print("I finished washing clothes")

async def drinking_coffee():
    print("I'm starting to drink coffee")
    await asyncio.sleep(3)
    print("I finished drinking coffee")


async def main():
    init = time.time()
    
    # method 1: using asyncio.create_task for each task
    """
    tasks = [
        asyncio.create_task(washing_clothes()),
        asyncio.create_task(drinking_lemonade()),
        asyncio.create_task(eating())
    ]

    await asyncio.gather(*tasks)
    """


    # method 2: using asyncio.gather directly
    """
    await asyncio.gather(
    washing_clothes(),
    drinking_lemonade(),
    eating()
    )
    """
    

    #method 3: Run tasks one-by-one but NOT waiting for them (fire & forget)
    """
    asyncio.create_task(washing_clothes())
    asyncio.create_task(drinking_lemonade())
    asyncio.create_task(eating())

    #Let the main keep working…
    await asyncio.sleep(25)  # just keep program alive
    """


    #method 4: Use TaskGroup (Python 3.11+)
    """
    async with asyncio.TaskGroup() as tg:
        tg.create_task(washing_clothes())
        tg.create_task(drinking_lemonade())
        tg.create_task(eating())
    """


    #method 5: Use asyncio.wait()
    tasks = [
    asyncio.create_task(washing_clothes()),
    asyncio.create_task(drinking_lemonade()),
    asyncio.create_task(eating())
]
    await asyncio.wait(tasks)

    end = time.time()
    print(f"All tasks completed in {end - init} seconds")


asyncio.run(main())