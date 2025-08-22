from .models import Category

def categories_list(request):
    cat_list = Category.objects.all()
    return dict(cat_list=cat_list)