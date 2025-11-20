"""
Programa para bajar imagenes de una liga proveniente de un arechivo de excel
columna C de excel debe tener numero de parte
columna k de excel debe contener la liga URL
archivo de excel se debe llamar  "Registros Ingram/ligas_foto.xlsx")
"""


import openpyxl
import pandas as pd
from urllib import request
from time import time
from datetime import datetime

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

result = []
def count_elapsed_time(f):
    """
    Decorator.
    Execute the function and calculate the elapsed time.
    Print the result to the standard output.
    """
    def wrapper():
        # Start counting.
        start_time = time()
        # Take the original function's return value.
        ret = f()
        # Calculate the elapsed time.
        elapsed_time = time() - start_time
        print("Elapsed time: %0.10f seconds." % elapsed_time)
        return ret
    
    return wrapper

@count_elapsed_time
def read_excel() -> list:
    global result, errors
    item_dict = {}
    # directorio donde leera archivo xlsx partiendo de Catalogo 2025
    dataframe = openpyxl.load_workbook("statics/files_to_read/ligas_foto.xlsx")

    # Define variable to read sheet
    dataframe1 = dataframe.active

    # Iterate the loop to read the cell values
    #result = []
    index = 0
    for row in range(1, dataframe1.max_row):
        record = [index]
        for col in dataframe1.iter_cols(1, dataframe1.max_column):
            record.append(col[row].value)
        if record[5] in item_dict :
            errors.append("error en linea: " + str(record[2]) + ". Item: " + str(record[5]) + ".  Repetido de linea: " + str(item_dict[record[5]]))
            continue
        else:
            item_dict[record[5]] = record[2]
        result.append(list(record))
        index += 1
    return result
    
@count_elapsed_time
def import_picts() -> None :
    cont = 0
    global result, errors
    for i in range(len(result)) :
        
        remote_url = result[i][13]          # el 13 es la columna 12 desde 0 del archivo de excel (url)
        local_file = "Imagenes/" + str(result[i][5]) + ".jpg"       # el 5 es la columna 4 desde 0 de excel (numero de parte)
        try :
            request.urlretrieve(remote_url, local_file)
            print(result[i][2]+ 2, remote_url, local_file)  # el 0 es el numero de renglon (index)
            cont += 1

        except :
            errors.append([result[i][2], result[i][5], result[i][13], "fallo descarga"])
    print(cont, "Archivos descargados")
    print(len(errors), "Errores encontrados")


@count_elapsed_time
def print_errors()-> None :
    global errors, init
    datos = pd.DataFrame(errors)
    # directorio para grabar archivo de erro.xlsx
    excel_writer = pd.ExcelWriter("errores_excel/erores_"+init+".xlsx")
    datos.to_excel(excel_writer, sheet_name="Hoja 1")
    excel_writer._save()
    print("Reporte generado")


now = datetime.now()
init = str(now.strftime('day_%d_%m_%Y_time_%H_%M'))
result = []
errors = []
read_excel()
import_picts()
print_errors()