import csv

def read(path):
    """Read csv file contents and yield a formatted line 

    Args:
        path: a path of a csv file to read
    
    Returns:
        A dict. {'header': associated column in a row}
    """
    with open(path, 'rU') as data:
        reader = csv.DictReader(data)
        for row in reader:
            yield row