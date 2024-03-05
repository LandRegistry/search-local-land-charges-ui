def calc_display_id(local_land_charge_id):
    characters = '0123456789BCDFGHJKLMNPQRSTVWXYZ'
    encoded = ''
    while local_land_charge_id > 0:
        local_land_charge_id, remainder = divmod(local_land_charge_id, 31)
        encoded = characters[remainder] + encoded
    return "LLC-{}".format(encoded)
