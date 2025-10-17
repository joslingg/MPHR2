from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import HealthRecord, Department, ExamType, HealthClassification
from .forms import HealthRecordForm
from django.urls import reverse

# -----------------------------
# QUẢN LÝ HỒ SƠ KHÁM SỨC KHỎE
# -----------------------------
def healthrecord_list(request):
    records = HealthRecord.objects.all().order_by('-year', 'full_name')
    return render(request, 'health_records/healthrecord_list.html', {'records': records})


def healthrecord_add(request):
    if request.method == 'POST':
        form = HealthRecordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã thêm hồ sơ khám sức khoẻ thành công.")
            return redirect('healthrecord_list')
    else:
        form = HealthRecordForm()

    return render(request, 'health_records/healthrecord_form.html', {'form': form, 'title': 'Thêm hồ sơ khám sức khoẻ'})

def health_record_detail(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    return render(request, 'health_records/health_record_detail.html', {'record': record})

def healthrecord_edit(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    if request.method == 'POST':
        form = HealthRecordForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật hồ sơ thành công.")
            return redirect('healthrecord_list')
    else:
        form = HealthRecordForm(instance=record)
    return render(request, 'health_records/healthrecord_form.html', {'form': form, 'title': 'Chỉnh sửa hồ sơ'})


def healthrecord_delete(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Đã xoá hồ sơ khám sức khoẻ.")
        return redirect('healthrecord_list')
    return render(request, 'health_records/confirm_delete.html', {'object': record, 'type': 'hồ sơ khám sức khoẻ'})


# -----------------------------
# DANH MỤC KHOA/PHÒNG
# -----------------------------
def department_list(request):
    departments = Department.objects.all()
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


# -----------------------------
# DANH MỤC LOẠI KHÁM
# -----------------------------
def examtype_list(request):
    examtypes = ExamType.objects.all()
    return render(request, 'health_records/examtype_list.html', {'examtypes': examtypes})


def examtype_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            ExamType.objects.create(name=name)
            messages.success(request, "Đã thêm Loại khám.")
            return redirect('examtype_list')
    return render(request, 'health_records/examtype_form.html', {'title': 'Thêm Loại khám'})


def examtype_edit(request, pk):
    exam = get_object_or_404(ExamType, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            exam.name = name
            exam.save()
            messages.success(request, "Đã cập nhật Loại khám.")
            return redirect('examtype_list')
    return render(request, 'health_records/examtype_form.html', {'title': 'Chỉnh sửa Loại khám', 'object': exam})


def examtype_delete(request, pk):
    exam = get_object_or_404(ExamType, pk=pk)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, "Đã xoá Loại khám.")
        return redirect('examtype_list')
    return render(request, 'health_records/confirm_delete.html', {'object': exam, 'type': 'Loại khám'})


# -----------------------------
# DANH MỤC PHÂN LOẠI SỨC KHỎE
# -----------------------------
def healthclass_list(request):
    classes = HealthClassification.objects.all()
    return render(request, 'health_records/healthclass_list.html', {'classes': classes})


def healthclass_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('description')
        if name:
            HealthClassification.objects.create(name=name, description=desc)
            messages.success(request, "Đã thêm Phân loại sức khoẻ.")
            return redirect('healthclass_list')
    return render(request, 'health_records/healthclass_form.html', {'title': 'Thêm Phân loại sức khoẻ'})


def healthclass_edit(request, pk):
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


def healthclass_delete(request, pk):
    obj = get_object_or_404(HealthClassification, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Đã xoá Phân loại sức khoẻ.")
        return redirect('healthclass_list')
    return render(request, 'health_records/confirm_delete.html', {'object': obj, 'type': 'Phân loại sức khoẻ'})

