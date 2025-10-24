from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import HealthRecord, Department, ExamType, HealthClassification
from .forms import HealthRecordForm
from django.urls import reverse
from django.db.models import Count
import json
from collections import Counter
import openpyxl
from .forms import ExcelImportForm
import os
from django.conf import settings
import datetime
import pandas as pd
from django.db import transaction

# -----------------------------
# TRANG CHỦ
# -----------------------------
def home(request):
    from .views import get_health_report_data
    stats = get_health_report_data()

    stats.update({
        'total_records': HealthRecord.objects.count(),
        'total_departments': Department.objects.count(),
        'total_examtypes': ExamType.objects.count(),
    })
    return render(request, 'health_records/home.html', stats)

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
        .values('gender')
        .annotate(count=Count('id'))
        .order_by('gender')
    )
    gender_labels = [item['gender'] or "Không rõ" for item in gender_qs]
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

def health_report(request):
    context = get_health_report_data()
    return render(request, 'health_records/report.html', context)

def _to_bool(val):
    """Chuyển giá trị excel sang boolean."""
    if val is None:
        return False
    v = str(val).strip().lower()
    return v in ("1", "x", "yes", "true", "có", "co", "y")

def _to_date(val):
    """Chuyển giá trị excel sang date (nếu được)."""
    if val is None:
        return None
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.date() if isinstance(val, datetime.datetime) else val
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None

def import_health_records(request):
    if request.method == "POST":
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]

            try:
                df = pd.read_excel(file)
            except Exception as e:
                messages.error(request, f"❌ Lỗi khi đọc file Excel: {e}")
                return redirect("healthrecord_list")

            required_columns = ["Mã nhân viên", "Họ và tên", "Khoa/Phòng"]
            for col in required_columns:
                if col not in df.columns:
                    messages.error(request, f"❌ Thiếu cột bắt buộc: {col}")
                    return redirect("healthrecord_list")

            errors = []
            new_records = []

            try:
                with transaction.atomic():  # đảm bảo all-or-nothing
                    for idx, row in df.iterrows():
                        row_num = idx + 2
                        ma_nv = str(row.get("Mã nhân viên", "")).strip()
                        full_name = str(row.get("Họ và tên", "")).strip()
                        department_name = str(row.get("Khoa/Phòng", "")).strip()

                        if not ma_nv or not full_name or not department_name:
                            errors.append(f"Dòng {row_num}: Thiếu Mã NV, Họ tên hoặc Khoa/Phòng.")
                            continue

                        department = Department.objects.filter(name__iexact=department_name).first()
                        if not department:
                            errors.append(f"Dòng {row_num}: Không tìm thấy Khoa/Phòng '{department_name}'.")
                            continue

                        # Loại khám
                        exam_type_name = str(row.get("Loại khám", "")).strip()
                        exam_type = None
                        if exam_type_name and exam_type_name.lower() != "nan":
                            exam_type = ExamType.objects.filter(name__iexact=exam_type_name).first()
                            if not exam_type:
                                errors.append(f"Dòng {row_num}: Không tìm thấy Loại khám '{exam_type_name}'.")
                                continue

                        # Phân loại sức khỏe
                        classification_name = str(row.get("Phân loại", "")).strip()
                        classification = None
                        if classification_name:
                            classification = HealthClassification.objects.filter(name__iexact=classification_name).first()
                            if not classification:
                                errors.append(f"Dòng {row_num}: Không tìm thấy Phân loại '{classification_name}'.")
                                continue

                        exam_date = _to_date(row.get("Ngày khám"))
                        status = "done" if exam_date else "pending"

                        record = HealthRecord(
                            ma_nv=ma_nv,
                            full_name=full_name,
                            birth_year=row.get("Năm sinh") if pd.notna(row.get("Năm sinh")) else None,
                            gender=row.get("Giới tính") if pd.notna(row.get("Giới tính")) else "Khác",
                            job_title=row.get("Chức danh nghề nghiệp") if pd.notna(row.get("Chức danh nghề nghiệp")) else "",
                            position=row.get("Chức vụ") if pd.notna(row.get("Chức vụ")) else "",
                            department=department,
                            exam_type=exam_type,
                            exam_date=exam_date,
                            health_classification=classification,
                            conclusion_text=row.get("Kết luận (nếu muốn nhập tay)") if pd.notna(row.get("Kết luận (nếu muốn nhập tay)")) else "Chưa khám",
                            year=row.get("Năm khám") if pd.notna(row.get("Năm khám")) else None,
                            vaccinated_influvac=_to_bool(row.get("Đã tiêm Influvac (Hà Lan)")),
                            vaccinated_vaxigrip=_to_bool(row.get("Đã tiêm Vaxigrip (Pháp)")),
                            vaccination_date=_to_date(row.get("Ngày tiêm chủng")),
                            height_cm=row.get("Chiều cao (cm)") if pd.notna(row.get("Chiều cao (cm)")) else None,
                            weight_kg=row.get("Cân nặng (kg)") if pd.notna(row.get("Cân nặng (kg)")) else None,
                            blood_pressure=row.get("Huyết áp (mmHg)") if pd.notna(row.get("Huyết áp (mmHg)")) else "",
                            clinic_name=row.get("Cơ sở khám") if pd.notna(row.get("Cơ sở khám")) else "",
                            group=row.get("Nhóm") if pd.notna(row.get("Nhóm")) else "",
                            note=row.get("Ghi chú") if pd.notna(row.get("Ghi chú")) else "",
                            status=status,
                        )
                        new_records.append(record)

                    if errors:
                        raise ValueError("\n".join(errors))

                    HealthRecord.objects.bulk_create(new_records)
                    messages.success(request, f"✅ Import thành công {len(new_records)} hồ sơ.")
                    return redirect("import_health_records")

            except ValueError as ve:
                messages.error(request, f"Lỗi dữ liệu:<br>{str(ve).replace(chr(10), '<br>')}")
            except Exception as e:
                messages.error(request, f"⚠️ Lỗi không xác định: {e}")

            return redirect("import_health_records")

    else:
        form = ExcelImportForm()

    return render(request, "health_records/import_excel.html", {"form": form})


def download_sample_healthrecord(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'samples', 'mau_import.xlsx')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='mau_import.xlsx')
