from django.urls import path
from .views import main
from .views import submit


urlpatterns = [
    path('main/', main, name='main'),  # '/main/' URL에 대한 뷰를 'main'으로 연결합니다.
    path('submit/', submit, name='submit'), # '/result/' URL에 대한 뷰를 'result'로 연결합니다.
    path('result/', submit, name='result')
]