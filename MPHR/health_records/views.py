# health_records/views.py
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Department, ExaminationType, HealthClassification,
    Employee, HealthRecord
)
from .forms import HealthRecordForm
import os
from django.conf import settings
from django.http import FileResponse
from django.db.models import Count
import json
from collections import Counter


def home(request):
    from .views import get_health_report_data
    stats = get_health_report_data()

    stats.update({
        'total_records': HealthRecord.objects.count(),
        'total_departments': Department.objects.count(),
        'total_examtypes': ExaminationType.objects.count(),
    })
    return render(request, 'health_records/home.html', stats)

def get_health_report_data():
    """Hàm xử lý và trả về dữ liệu thống kê hồ sơ sức khoẻ"""

    # 1. Theo phân loại sức khoẻ
    hc_qs = (
        HealthRecord.objects
        .values('health_classification__name')
        .annotate(count=Count('id'))
        .order_by('health_classification__name')
    )
    health_labels = [item['health_classification__name'] or "Chưa phân loại" for item in hc_qs]
    health_counts = [item['count'] for item in hc_qs]

    # 2. Theo kết luận (dùng Counter để đảm bảo tính chính xác của property `conclusion`)
    records = HealthRecord.objects.all()
    conclusion_counter = Counter((r.conclusion or "").strip() or "Không có kết luận" for r in records)
    conclusion_labels = list(conclusion_counter.keys())
    conclusion_counts = list(conclusion_counter.values())

    # 3. Theo giới tính
    gender_qs = (
        HealthRecord.objects
        .values('employee__gender')
        .annotate(count=Count('id'))
        .order_by('employee__gender')
    )
    gender_labels = [item['employee__gender'] or "Không rõ" for item in gender_qs]
    gender_counts = [item['count'] for item in gender_qs]

    # Trả về dữ liệu đã sẵn sàng render hoặc chuyển sang JSON
    return {
        'dept_labels': json.dumps(health_labels),
        'dept_counts': json.dumps(health_counts),
        'conclusion_labels': json.dumps(conclusion_labels),
        'conclusion_counts': json.dumps(conclusion_counts),
        'gender_labels': json.dumps(gender_labels),
        'gender_counts': json.dumps(gender_counts),
    }

# ========== NHÂN VIÊN ==========

def employee_list(request):
    employees = Employee.objects.select_related('department').order_by('full_name')
    return render(request, 'health_records/employee_list.html', {'employees': employees})


def employee_add(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        code = request.POST.get('code')
        full_name = request.POST.get('full_name')
        birth_year = request.POST.get('birth_year') or None
        gender = request.POST.get('gender') or None
        job_title = request.POST.get('job_title')
        position = request.POST.get('position')
        dept_id = request.POST.get('department')

        if code and full_name:
            department = Department.objects.filter(id=dept_id).first()
            Employee.objects.create(
                code=code,
                full_name=full_name,
                birth_year=birth_year,
                gender=gender,
                job_title=job_title,
                position=position,
                department=department
            )
            messages.success(request, "Đã thêm Nhân viên.")
            return redirect('employee_list')

    return render(request, 'health_records/employee_form.html', {
        'title': 'Thêm Nhân viên',
        'departments': departments
    })


def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    departments = Department.objects.all()

    if request.method == 'POST':
        emp.code = request.POST.get('code')
        emp.full_name = request.POST.get('full_name')
        emp.birth_year = request.POST.get('birth_year') or None
        emp.gender = request.POST.get('gender') or None
        emp.job_title = request.POST.get('job_title')
        emp.position = request.POST.get('position')
        dept_id = request.POST.get('department')
        emp.department = Department.objects.filter(id=dept_id).first()
        emp.save()

        messages.success(request, "Đã cập nhật Nhân viên.")
        return redirect('employee_list')

    return render(request, 'health_records/employee_form.html', {
        'title': 'Chỉnh sửa Nhân viên',
        'employee': emp,
        'departments': departments
    })


def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        emp.delete()
        messages.success(request, "Đã xoá Nhân viên.")
        return redirect('employee_list')
    return render(request, 'health_records/confirm_delete.html', {
        'object': emp,
        'type': 'Nhân viên'
    })


# ========== DANH MỤC CƠ BẢN ==========

def department_list(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'health_records/department_list.html', {'departments': departments})


def department_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Department.objects.create(name=name)
            messages.success(request, "Đã thêm Khoa/Phòng.")
            return redirect('department_list')
    return render(request, 'health_records/department_form.html', {'title': 'Thêm Khoa/Phòng'})


def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            dept.name = name
            dept.save()
            messages.success(request, "Đã cập nhật Khoa/Phòng.")
            return redirect('department_list')
    return render(request, 'health_records/department_form.html', {'title': 'Chỉnh sửa Khoa/Phòng', 'object': dept})


def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, "Đã xoá Khoa/Phòng.")
        return redirect('department_list')
    return render(request, 'health_records/confirm_delete.html', {'object': dept, 'type': 'Khoa/Phòng'})


# ========== LOẠI KHÁM ==========

def examinationtype_list(request):
    types = ExaminationType.objects.all().order_by('name')
    return render(request, 'health_records/examinationtype_list.html', {'examinationtypes': types})


def examinationtype_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            ExaminationType.objects.create(name=name)
            messages.success(request, "Đã thêm Loại khám.")
            return redirect('examinationtype_list')
    return render(request, 'health_records/examinationtype_form.html', {'title': 'Thêm Loại khám'})


def examinationtype_edit(request, pk):
    exam = get_object_or_404(ExaminationType, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            exam.name = name
            exam.save()
            messages.success(request, "Đã cập nhật Loại khám.")
            return redirect('examinationtype_list')
    return render(request, 'health_records/examinationtype_form.html', {'title': 'Chỉnh sửa Loại khám', 'object': exam})


def examinationtype_delete(request, pk):
    exam = get_object_or_404(ExaminationType, pk=pk)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, "Đã xoá Loại khám.")
        return redirect('examtype_list')
    return render(request, 'health_records/confirm_delete.html', {'object': exam, 'type': 'Loại khám'})



# ========== PHÂN LOẠI SỨC KHỎE ==========

def healthclasses_list(request):
    classes = HealthClassification.objects.all().order_by('name')
    return render(request, 'health_records/healthclass_list.html', {'classes': classes})


def healthclasses_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('description')
        if name:
            HealthClassification.objects.create(name=name, description=desc)
            messages.success(request, "Đã thêm Phân loại sức khoẻ.")
            return redirect('healthclasses_list')
    return render(request, 'health_records/healthclass_form.html', {'title': 'Thêm Phân loại sức khoẻ'})


def healthclasses_edit(request, pk):
    obj = get_object_or_404(HealthClassification, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('description')
        if name:
            obj.name = name
            obj.description = desc
            obj.save()
            messages.success(request, "Đã cập nhật Phân loại sức khoẻ.")
            return redirect('healthclass_list')
    return render(request, 'health_records/healthclass_form.html', {'title': 'Chỉnh sửa Phân loại sức khoẻ', 'object': obj})


def healthclasses_delete(request, pk):
    obj = get_object_or_404(HealthClassification, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Đã xoá Phân loại sức khoẻ.")
        return redirect('healthclass_list')
    return render(request, 'health_records/confirm_delete.html', {'object': obj, 'type': 'Phân loại sức khoẻ'})


# ========== HỒ SƠ SỨC KHỎE ==========

def healthrecord_list(request):
    records = HealthRecord.objects.select_related(
    'employee', 'employee__department', 'examination_type', 'health_classification'
)

    return render(request, 'health_records/healthrecord_list.html', {'records': records})


def healthrecord_detail(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    return render(request, 'health_records/healthrecord_detail.html', {'record': record})


def healthrecord_add(request):
    form = HealthRecordForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Đã thêm hồ sơ sức khỏe.")
        return redirect('healthrecord_list')
    return render(request, 'health_records/healthrecord_form.html', {'form': form, 'title': 'Thêm hồ sơ sức khỏe'})


def healthrecord_edit(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    form = HealthRecordForm(request.POST or None, request.FILES or None, instance=record)
    if form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật hồ sơ sức khỏe.")
        return redirect('healthrecord_list')
    return render(request, 'health_records/healthrecord_form.html', {'form': form, 'title': 'Cập nhật hồ sơ sức khỏe'})


def healthrecord_delete(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    record.delete()
    messages.success(request, "Đã xóa hồ sơ sức khỏe.")
    return redirect('healthrecord_list')


# ========== IMPORT EXCEL ==========

def healthrecord_import(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        df = pd.read_excel(file)
        missing_employees = []

        for _, row in df.iterrows():
            emp_code = str(row.get('Mã nhân viên')).strip()
            try:
                employee = Employee.objects.get(code=emp_code)
            except Employee.DoesNotExist:
                missing_employees.append(emp_code)
                continue

            dept = Department.objects.filter(name=row.get('Khoa/Phòng')).first()
            examination_type = ExaminationType.objects.filter(name=row.get('Loại khám')).first()
            classification = HealthClassification.objects.filter(name=row.get('Phân loại sức khoẻ')).first()

            HealthRecord.objects.create(
                employee=employee,
                year=row.get('Năm khám'),
                exam_date=row.get('Ngày khám'),
                clinic_name=row.get('Cơ sở khám'),
                height_cm=row.get('Chiều cao (cm)'),
                weight_kg=row.get('Cân nặng (kg)'),
                blood_pressure=row.get('Huyết áp (mmHg)'),
                health_classification=classification,
                conclusion_text=row.get('Kết luận (nếu muốn nhập tay)'),
                department=dept,
                examination_type=examination_type,
                vaccinated=(str(row.get('Đã tiêm vắc-xin')).strip().lower() in ['x', 'có', 'yes', '1', 'true']),
                vaccine_name=row.get('Tên vắc-xin'),
                vaccine_date=row.get('Ngày tiêm chủng'),
                note=row.get('Ghi chú'),
            )

        if missing_employees:
            messages.warning(request, f"Các mã nhân viên không tồn tại: {', '.join(missing_employees)}")
        else:
            messages.success(request, "Đã import thành công tất cả hồ sơ.")
        return redirect('healthrecord_list')

    return render(request, 'health_records/healthrecord_import.html', {'title': 'Import hồ sơ sức khỏe từ Excel'})

def download_sample_healthrecord(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'samples', 'mau_import_hssk.xlsx')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='mau_import_hssk.xlsx')

# ========== IMPORT NHÂN VIÊN ==========

def employee_import(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        df = pd.read_excel(file)

        for index, row in df.iterrows():
            emp_code = row.get('Mã nhân viên')
            full_name = row.get('Họ và tên')

            # Validate bắt buộc
            if pd.isna(emp_code) or pd.isna(full_name):
                return render(request, 'health_records/employee_import.html', {
                    'title': 'Import danh sách nhân viên',
                    'error': f"❌ Dòng {index+2}: Thiếu mã nhân viên hoặc họ tên."
                })

            emp_code = str(emp_code).strip()
            full_name = str(full_name).strip()

            # Kiểm tra Khoa/Phòng
            dept_name = row.get('Khoa/Phòng')
            if pd.isna(dept_name):
                department = None
            else:
                dept_name = str(dept_name).strip()
                department = Department.objects.filter(name=dept_name).first()
                if not department:
                    return render(request, 'health_records/employee_import.html', {
                        'title': 'Import danh sách nhân viên',
                        'error': f"❌ Dòng {index+2}: Khoa/Phòng '{dept_name}' chưa tồn tại trong hệ thống."
                    })

            # Giới tính
            gender = row.get('Giới tính')
            if pd.isna(gender):
                gender = None
            else:
                gender = str(gender).strip().capitalize()
                if gender not in ['Nam', 'Nữ']:
                    gender = None

            # Các ô optional
            birth_year = row.get('Năm sinh')
            birth_year = None if pd.isna(birth_year) else int(birth_year)

            job_title = row.get('Chức danh nghề nghiệp')
            job_title = None if pd.isna(job_title) else str(job_title).strip()

            position = row.get('Chức vụ')
            position = None if pd.isna(position) else str(position).strip()

            # Tạo hoặc cập nhật
            Employee.objects.update_or_create(
                code=emp_code,
                defaults={
                    'full_name': full_name,
                    'birth_year': birth_year,
                    'gender': gender,
                    'job_title': job_title,
                    'position': position,
                    'department': department,
                }
            )

        messages.success(request, "✅ Import thành công danh sách nhân viên.")
        return redirect('employee_list')

    return render(request, 'health_records/employee_import.html', {
        'title': 'Import danh sách nhân viên'
    })


def download_sample_employee(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'samples', 'mau_import_nv.xlsx')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='mau_import_nv.xlsx')
