from django.db.models import Sum
from django.http import HttpResponse


def download_txt_cart(carts):
    response = HttpResponse(content_type='text/plain')
    filename = u'shopping-cart.txt'
    response['Content-Disposition'] = f'attachment; filename={filename}'

    ingredients_total = carts.values(
        'recipe__ingredients__name',
        'recipe__ingredients__measurement_unit'
    ).annotate(
        total_amount=Sum('recipe__ingredientrecipe__amount')
    ).order_by('recipe__ingredients__name')

    for ingredient in ingredients_total:
        response.write(
            f'{ingredient["recipe__ingredients__name"]} '
            f'({ingredient["recipe__ingredients__measurement_unit"]}) — '
            f'{ingredient["total_amount"]}\n'
        )

    return response
