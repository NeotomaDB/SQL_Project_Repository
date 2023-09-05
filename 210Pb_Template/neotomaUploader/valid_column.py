import datetime

def is_valid_date(value):
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def is_numeric(value):
    '''check if the values can be cast properly as numbers'''
    try:
        int(value)
        return True
    except ValueError:
        try:
            float(value)
            return True
        except ValueError:
            return False


def valid_column(pointer):
    response = {'message': []}
    allowed_types = {
        'string': str,
        'number': is_numeric,
        'date': is_valid_date
    }
    value_type = pointer.get('type')
    values_list = pointer.get('values')
    if callable(allowed_types[value_type]):
        # If the type is a date check, call the function for each value
        result = all(allowed_types[value_type](value) for value in values_list)
    else:
        # If the type is a standard Python type, perform the isinstance check
        result = all(isinstance(value, allowed_types[value_type]) for value in values_list)
    if result is False:
        print(pointer)
        response['message'].append(f'✗ {pointer["column"]} is not properly formatted.')
        response['message'] = ''.join(response['message'])
    return response['message']
