from django.shortcuts import render
from . import scrape
# Create your views here.

def homepage(request):
    return render(request=request, template_name='main/home.html')

def search(request):
    res_set = request.GET.copy()
    query = res_set['q']

    sort_method = 'bm'
    allowUsed = True

    if 's' in res_set:
        sort_method = res_set['s']
    if 'c' in res_set:
        match res_set['c']:
            case 'n+u':
                allowUsed = True
            case 'n':
                allowUsed = False

    print(sort_method)
    
    return render(request=request, 
                  template_name='main/search.html',
                  context={'query': query,
                            'products': scrape.get_products(query, 15, sort_method, allowUsed),
                            'sort_method': sort_method})
