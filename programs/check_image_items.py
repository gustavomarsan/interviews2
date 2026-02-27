"""
This script reads an Excel file containing a list of items and check if there is an image in
/programs/static/photos_api with the name of the item + ".jpg". Then return a excel file with 2 colums
one with the item name and the other with YES if the image exists and NO if it doesn't.

"""
from functools import wraps
from serpapi import GoogleSearch
import openpyxl
import pandas as pd
from time import time
from datetime import datetime
import json
import ssl
import os
import aiohttp
import asyncio
from pathlib import Path
from file_manager import FileManager

#ssl._create_default_https_context = ssl._create_unverified_context
BASE_DIR = Path(__file__).resolve().parent.parent


def count_elapsed_time(f):
    @wraps(f)
    async def async_wrapper(*args, **kwargs):
        start_time = time()
        ret = await f(*args, **kwargs)
        elapsed_time = time() - start_time
        print(f"Task: {f.__name__}. Elapsed time: %0.4f seconds." % elapsed_time)
        return ret

    @wraps(f)   
    def sync_wrapper(*args, **kwargs):
        start_time = time()
        ret = f(*args, **kwargs)
        elapsed_time = time() - start_time
        print(f"Task: {f.__name__}. Elapsed time: %0.4f seconds." % elapsed_time)
        return ret
    return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper

@count_elapsed_time
def read_excel(result) -> None :
    excel_path = BASE_DIR / "programs/static/files_to_read/list_to_check.xlsx"

    with FileManager(excel_path, "rb") as file:
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        for row in sheet.iter_rows(min_row=2, values_only=True):
            result.append(row[0])   # Item

    return

@count_elapsed_time
def check_file(result, init) -> None :
    checklist = []
    for i, item in enumerate(result):
        image_path = BASE_DIR / "programs/static/photos_api" / f"{item}.jpg"
        exists = image_path.is_file()
        checklist.append((str(item)+".jpg" if exists else "", "YES" if exists else "NO"))
        print(f"line {i+1} - {item} - {'YES' if exists else 'NO'}")


    # Save the results to an excel file
    datos = pd.DataFrame(checklist, columns=["Item", "Image Exists"])
    results_path = BASE_DIR / "programs/static/results_excel/"
    results_path.mkdir(parents=True, exist_ok=True)
    file_path = results_path / f"check_list_{init}.xlsx"

    with FileManager(file_path, "wb") as file:
        with pd.ExcelWriter(file, engine='openpyxl') as writer:
            datos.to_excel(writer, sheet_name=init, index=False)


@count_elapsed_time
async def main():
    now = datetime.now()
    init = str(now.strftime('day_%d_%m_%Y_time_%H_%M'))
    result = []
    read_excel(result)

    if result:
        check_file(result, init)

    else:
        print("No items found in the Excel file.")



if __name__ == "__main__":
    asyncio.run(main())