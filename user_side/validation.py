import re

def validate_address_data(post_data):
    errors = {}

    address_line = post_data.get('address_line', '').strip()
    city = post_data.get('city', '').strip()
    state = post_data.get('state', '').strip()
    country = post_data.get('country', '').strip()
    postal_code = post_data.get('postal_code', '').strip()
    phone_number = post_data.get('phone_number', '').strip()
    is_default = post_data.get('is_default') == 'on'

    # Address Line
    if not address_line:
        errors['address_line'] = 'Address line is required.'
    elif not (5 <= len(address_line) <= 100):
        errors['address_line'] = 'Address line must be between 5 and 100 characters.'
    elif re.search(r'[^a-zA-Z0-9\s,.-]', address_line):
        errors['address_line'] = 'Address line contains invalid characters.'

    # City
    if not city:
        errors['city'] = 'City is required.'
    elif len(city) > 50:
        errors['city'] = 'City name is too long (max 50 characters).'
    elif not re.match(r'^[a-zA-Z\s\-]+$', city):
        errors['city'] = 'City must only contain letters, spaces, or hyphens.'

    # State
    if not state:
        errors['state'] = 'State is required.'
    elif len(state) > 50:
        errors['state'] = 'State name is too long (max 50 characters).'
    elif not re.match(r'^[a-zA-Z\s\-]+$', state):
        errors['state'] = 'State must only contain letters, spaces, or hyphens.'

    # Country
    if not country:
        errors['country'] = 'Country is required.'
    elif len(country) > 50:
        errors['country'] = 'Country name is too long (max 50 characters).'
    elif not re.match(r'^[a-zA-Z\s\-]+$', country):
        errors['country'] = 'Country must only contain letters, spaces, or hyphens.'

    # Postal Code
    if not postal_code:
        errors['postal_code'] = 'Postal code is required.'
    elif not re.match(r'^\d{4,10}$', postal_code):
        errors['postal_code'] = 'Postal code must be 4–10 digits.'

    # Phone Number (same everywhere)
    if not phone_number:
        errors['phone_number'] = 'Phone number is required.'
    elif not re.match(r'^\+\d{1,4}\d{6,10}$', phone_number):
        errors['phone_number'] = (
            'Phone number must start with +countrycode and contain 6–10 digits.'
        )

    cleaned_data = {
        'address_line': address_line,
        'city': city,
        'state': state,
        'country': country,
        'postal_code': postal_code,
        'phone_number': phone_number,
        'is_default': is_default,
    }

    return errors, cleaned_data

