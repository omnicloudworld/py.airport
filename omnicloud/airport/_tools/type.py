
def _convert_to_bool(string):
    return bool(int(string)) if string.isdigit() else string.lower() in ['true', 'yes', 'on', '1']
