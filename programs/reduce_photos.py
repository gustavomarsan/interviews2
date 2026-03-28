"""
This script reduces photos in dir nnnnnn to the desire list in input excel file. It reads the "Fotos Finales.xlsx" file
and keep in the dir if photo is needed and moved to the "Fotos sobrantes" dir is photo is not needed.
It also return a list if the photos that are needed but not found in the dir.

"""
from functools import wraps
import openpyxl
from time import time
import os
from pathlib import Path
from file_manager import FileManager

BASE_DIR = Path(__file__).resolve().parent.parent


def count_elapsed_time(f):
    @wraps(f)   
    def wrapper(*args, **kwargs):
        start_time = time()
        ret = f(*args, **kwargs)
        elapsed_time = time() - start_time
        print(f"Task: {f.__name__}. Elapsed time: %0.4f seconds." % elapsed_time)
        return ret
    return wrapper


@count_elapsed_time
def read_excel(result) -> None :
    excel_path = BASE_DIR / "programs/static/files_to_read/Fotos Finales.xlsx"

    with FileManager(excel_path, "rb") as file:
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        for row in sheet.iter_rows(values_only=True):
            result.append(row[0])   # Item
    my_set = set(result)

    diff = len(my_set) != len(result)
    if diff:
        print(f"Hay {diff} elementos duplicados en el archivo Excel.")
    else:
        print("No hay elementos duplicados en el archivo Excel.")
        print(f"Total de elementos en lista: {len(my_set)}")
    
    

    return my_set

@count_elapsed_time
def move_no_needed_photos(my_set):
    photos_dir = BASE_DIR / "programs/static/photos_api"
    photos = os.listdir(photos_dir)
    #avoid hidden files and folders in the dir    
    photos = [photo for photo in photos if not photo.startswith('.') and not os.path.isdir(photos_dir / photo)]
    sobrantes_dir = photos_dir / "Fotos sobrantes"
    sobrantes_dir.mkdir(exist_ok=True)      # create the "Fotos sobrantes" dir if it doesn't exist
    moved= 0
    deleted = 0
    exist = 0
    for photo in photos:
        if photo not in my_set:
            print(photo)
            if os.path.exists(sobrantes_dir / photo):
                print(f"La foto {photo} ya existe en el directorio 'Fotos sobrantes'. Será eliminada.")
                os.remove(photos_dir / photo)
                deleted += 1
                continue
            try: 
                os.rename(photos_dir / photo, sobrantes_dir / photo)
                moved += 1
            except: 
                    print(f"Error moviendo foto: {photo}")
        else:
            exist += 1
    print(f"{moved} Fotos movidas a directorio 'Fotos sobrantes'.")
    print(f"{deleted} Fotos borradas del directorio original.")
    print(f"{exist} Fotos existen en el directorio original.")
    final_photos = os.listdir(photos_dir)
    final_photos = [photo for photo in final_photos if not photo.startswith('.') and not os.path.isdir(photos_dir / photo)]
    print(f"Quedan {len(final_photos)} fotos en el directorio original.")


print(BASE_DIR)
result = []
my_set = read_excel(result)
#move_no_needed_photos(my_set)