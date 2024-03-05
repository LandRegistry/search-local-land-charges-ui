def format_fee_for_display(fee_in_pence):
    fee_pounds = fee_in_pence[:-2]
    fee_pence = fee_in_pence[-2:]
    if fee_pence == "00":
        search_fee = "{}".format(fee_pounds)
    else:
        search_fee = "{}.{}".format(fee_pounds, fee_pence)

    return search_fee


def format_fee_for_gov_pay(fee_in_pence):
    # Because environment variables are strings, convert to int for gov pay. If not valid default to 15 pounds
    try:
        gov_pay_fee = int(fee_in_pence)
    except ValueError:
        gov_pay_fee = 1500

    return gov_pay_fee
