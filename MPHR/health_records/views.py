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
    """
    Import file Excel (.xlsx) theo header mẫu.
    KHÔNG tạo mới dữ liệu liên kết (Department, ExamType, HealthClassification).
    Nếu không tìm thấy FK -> bỏ qua dòng và báo lỗi cụ thể.
    """
    if request.method == "POST":
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            try:
                wb = openpyxl.load_workbook(file, data_only=True)
                ws = wb.active

                headers = [str(c.value).strip() if c.value else "" for c in ws[1]]

                col_map = {
                    "Mã nhân viên": "ma_nv",
                    "Họ và tên": "full_name",
                    "Năm sinh": "birth_year",
                    "Giới tính": "gender",
                    "Chức danh nghề nghiệp": "job_title",
                    "Chức vụ": "position",
                    "Khoa/Phòng": "department",
                    "Đã tiêm Influvac (Hà Lan)": "vaccinated_influvac",
                    "Đã tiêm Vaxigrip (Pháp)": "vaccinated_vaxigrip",
                    "Ngày tiêm chủng": "vaccination_date",
                    "Năm khám": "year",
                    "Ngày khám": "exam_date",
                    "Loại khám": "exam_type",
                    "Cơ sở khám": "clinic_name",
                    "Chiều cao (cm)": "height_cm",
                    "Cân nặng (kg)": "weight_kg",
                    "Huyết áp (mmHg)": "blood_pressure",
                    "Phân loại sức khoẻ": "health_classification",
                    "Kết luận (nếu muốn nhập tay)": "conclusion_text",
                    "Nhóm": "group",
                    "Ghi chú": "note",
                    "File kết quả (PDF)": "result_file",
                }

                col_index = {}
                for i, h in enumerate(headers):
                    if h in col_map:
                        col_index[col_map[h]] = i

                created = 0
                skipped = 0
                errors = []

                for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    try:
                        if not row or all(v is None for v in row):
                            continue

                        data = {key: row[idx] if idx < len(row) else None for key, idx in col_index.items()}
                        if not data.get("full_name"):
                            skipped += 1
                            errors.append(f"Dòng {row_idx}: Thiếu 'Họ và tên'.")
                            continue

                        # 🔎 Kiểm tra tồn tại Department
                        dept_name = (data.get("department") or "").strip()
                        dept = None
                        if dept_name:
                            dept = Department.objects.filter(name__iexact=dept_name).first()
                            if not dept:
                                skipped += 1
                                errors.append(f"Dòng {row_idx}: Khoa/Phòng '{dept_name}' chưa có trong hệ thống.")
                                continue

                        # 🔎 Kiểm tra tồn tại ExamType
                        examtype_name = (data.get("exam_type") or "").strip()
                        examtype = None
                        if examtype_name:
                            examtype = ExamType.objects.filter(name__iexact=examtype_name).first()
                            if not examtype:
                                skipped += 1
                                errors.append(f"Dòng {row_idx}: Loại khám '{examtype_name}' chưa có trong hệ thống.")
                                continue

                        # 🔎 Kiểm tra tồn tại HealthClassification
                        hc_name = (data.get("health_classification") or "").strip()
                        hc_obj = None
                        if hc_name:
                            hc_obj = HealthClassification.objects.filter(name__iexact=hc_name).first()
                            if not hc_obj:
                                skipped += 1
                                errors.append(f"Dòng {row_idx}: Phân loại sức khoẻ '{hc_name}' chưa có trong hệ thống.")
                                continue

                        hr = HealthRecord.objects.create(
                            ma_nv=data.get("ma_nv"),
                            full_name=data.get("full_name"),
                            birth_year=int(data["birth_year"]) if data.get("birth_year") else None,
                            gender=data.get("gender"),
                            job_title=data.get("job_title"),
                            position=data.get("position"),
                            department=dept,
                            vaccinated_influvac=_to_bool(data.get("vaccinated_influvac")),
                            vaccinated_vaxigrip=_to_bool(data.get("vaccinated_vaxigrip")),
                            vaccination_date=_to_date(data.get("vaccination_date")),
                            year=int(data["year"]) if data.get("year") else None,
                            exam_date=_to_date(data.get("exam_date")),
                            exam_type=examtype,
                            clinic_name=data.get("clinic_name"),
                            height_cm=data.get("height_cm"),
                            weight_kg=data.get("weight_kg"),
                            blood_pressure=data.get("blood_pressure"),
                            health_classification=hc_obj,
                            conclusion_text=data.get("conclusion_text"),
                            group=data.get("group"),
                            note=data.get("note"),
                        )
                        created += 1

                    except Exception as e_row:
                        skipped += 1
                        errors.append(f"Dòng {row_idx}: {e_row}")

                if created:
                    messages.success(request, f"✅ Đã nhập {created} hồ sơ thành công.")
                if errors:
                    msg_err = f"⚠️ Có {len(errors)} dòng lỗi. Một số ví dụ:\n" + "\n".join(errors[:10])
                    messages.error(request, msg_err)

            except Exception as e:
                messages.error(request, f"❌ Lỗi khi đọc file: {e}")

    else:
        form = ExcelImportForm()

    return render(request, "health_records/import_excel.html", {"form": form})

def download_sample_healthrecord(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'samples', 'mau_import.xlsx')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='mau_import.xlsx')
