def is_valid_number(s):
    try:
        # Attempt to convert to float (works for both integers and floats)
        float(s)
        return True
    except ValueError:
        return False

def is_valid_word(text):
    return text.isalnum() and len(text.split()) == 1

def split_2_parts(text):
    parts = text.split(maxsplit=1)
    if len(parts) == 1:
        return parts[0], ""
    else:
        return parts[0], parts[1]
    
            
def split_3_parts(text):
    parts = text.split(maxsplit=2)
    if len(parts) == 1:
        return parts[0], "", "" 
    elif len(parts) == 2:
        return parts[0], parts[1], ""
    else:
        return parts[0], parts[1], parts[2]
    