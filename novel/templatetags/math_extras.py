
from django import template


register = template.Library()

@register.filter
def ratings_calculate(novel):
    if novel.novel_ratings.count() > 0:
        return fmean(
            [rating.average_rating for rating in novel.novel_ratings.all()]
        )
    return 0
    