import csv, io

def is_valid_number(s):
    try:
        # Attempt to convert to float (works for both integers and floats)
        float(s)
        return True
    except ValueError:
        return False
      
def split_3_parts(text):
    parts = text.split(maxsplit=2)
    if len(parts) == 1:
        return parts[0], "", "" 
    elif len(parts) == 2:
        return parts[0], parts[1], ""
    else:
        return parts[0], parts[1], parts[2]
      
def generate_doc(data):
    """
    csv module can write data in io.StringIO buffer only, python-telegram-bot library can send files 
    only from io.BytesIO bufferwe need to convert StringIO to BytesIO, extract csv-string, convert 
    it to bytes and write to buffer.
    """
    
    string_buffer = io.StringIO()
    csv.writer(string_buffer).writerows(data)
    string_buffer.seek(0)

    bytes_buffer = io.BytesIO()
    bytes_buffer.write(string_buffer.getvalue().encode())
    bytes_buffer.seek(0)

    # set a filename with file's extension
    bytes_buffer.name = f'spending_report.csv'
    return bytes_buffer