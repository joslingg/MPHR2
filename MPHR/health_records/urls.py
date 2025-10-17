from django.urls import path
from . import views

urlpatterns = [
    # === Hồ sơ khám sức khoẻ ===
    path('', views.healthrecord_list, name='healthrecord_list'),
    path('add/', views.healthrecord_add, name='healthrecord_add'),
    path('<int:pk>/edit/', views.healthrecord_edit, name='healthrecord_edit'),
    path('<int:pk>/delete/', views.healthrecord_delete, name='healthrecord_delete'),
    path('health-record/<int:pk>/', views.health_record_detail, name='health_record_detail'),


    # === Danh mục Khoa/Phòng ===
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_add, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # === Danh mục Loại khám ===
    path('examtypes/', views.examtype_list, name='examtype_list'),
    path('examtypes/add/', views.examtype_add, name='examtype_add'),
    path('examtypes/<int:pk>/edit/', views.examtype_edit, name='examtype_edit'),
    path('examtypes/<int:pk>/delete/', views.examtype_delete, name='examtype_delete'),

    # === Danh mục Phân loại sức khoẻ ===
    path('healthclasses/', views.healthclass_list, name='healthclass_list'),
    path('healthclasses/add/', views.healthclass_add, name='healthclass_add'),
    path('healthclasses/<int:pk>/edit/', views.healthclass_edit, name='healthclass_edit'),
    path('healthclasses/<int:pk>/delete/', views.healthclass_delete, name='healthclass_delete'),
]
