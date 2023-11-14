import csv

from django.http import HttpResponse


def download_csv_cart(carts):
    response = HttpResponse(content_type='text/csv')
    filename = u'shopping-cart'
    response[
        'Content-Disposition'
    ] = f'attachment; filename={filename}'
    writer = csv.writer(
        response,
        delimiter=';',
        quotechar='"',
        quoting=csv.QUOTE_ALL
    )
    for cart in carts:
        writer.writerow([cart.recipe])

    return response
