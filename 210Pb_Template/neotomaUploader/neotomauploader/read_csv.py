import csv

def read_csv(filename):
    """_Read CSV file and return a structured dict_
    """
    with open(filename) as f:
        file_data = csv.reader(f)
        headers = next(file_data)
        return [dict(zip(headers,i)) for i in file_data]
