# health_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ
    path("", views.home, name="home"),

    # --- Khoa/Phòng ---
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_add, name="department_add"),
    path("departments/<int:pk>/edit/", views.department_edit, name="department_edit"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department_delete"),

    # --- Loại khám ---
    path("examtypes/", views.examinationtype_list, name="examinationtype_list"),
    path("examtypes/add/", views.examinationtype_add, name="examinationtype_add"),
    path("examtypes/<int:pk>/edit/", views.examinationtype_edit, name="examinationtype_edit"),
    path("examtypes/<int:pk>/delete/", views.examinationtype_delete, name="examinationtype_delete"),

    # --- Phân loại sức khoẻ ---
    path("healthclasses/", views.healthclasses_list, name="healthclasses_list"),
    path("healthclasses/add/", views.healthclasses_add, name="healthclasses_add"),
    path("healthclasses/<int:pk>/edit/", views.healthclasses_edit, name="healthclasses_edit"),
    path("healthclasses/<int:pk>/delete/", views.healthclasses_delete, name="healthclasses_delete"),

    # --- Nhân viên ---
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_add, name="employee_add"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),

    # --- Hồ sơ sức khỏe ---
    path("records/", views.healthrecord_list, name="healthrecord_list"),
    path("records/add/", views.healthrecord_add, name="healthrecord_add"),
    path("records/<int:pk>/edit/", views.healthrecord_edit, name="healthrecord_edit"),
    path("records/<int:pk>/delete/", views.healthrecord_delete, name="healthrecord_delete"),
    path("records/<int:pk>/", views.healthrecord_detail, name="healthrecord_detail"),

    
     # === Import excel ===
    path('import-excel/', views.healthrecord_import, name='healthrecord_import'),
    path('download-sample/', views.download_sample_healthrecord, name='download_sample_healthrecord'),
    path("employees/import/", views.employee_import, name="employee_import"),
    path("employees/import/sample/", views.download_sample_employee, name="download_sample_employee"),


]
