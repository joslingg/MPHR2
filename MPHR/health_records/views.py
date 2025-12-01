# health_records/views.py
from datetime import datetime
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Department, ExaminationType, HealthClassification,
    Employee, HealthRecord, EmployeeTemp
)
from .forms import HealthRecordForm
import os, io, re
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.db.models import Count
import json
from collections import Counter
import uuid
from django.db import transaction
from django.template.loader import render_to_string
from django.http import JsonResponse
import traceback
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import HealthRecordTemp
from django.utils import timezone
from urllib.parse import urlencode

# ========== TRANG CHỦ VÀ BÁO CÁO ==========
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
    # --- Lấy các tham số lọc / tìm kiếm / sắp xếp ---
    search_query = request.GET.get("q", "").strip()
    department_id = request.GET.get("department", "")
    job_title = request.GET.get("job_title", "")
    sort = request.GET.get("sort", "code")
    direction = request.GET.get("dir", "asc")

    # --- Query cơ bản ---
    employees = Employee.objects.select_related("department").all()

    # --- Lọc theo từ khóa ---
    if search_query:
        employees = employees.filter(
            Q(code__icontains=search_query) |
            Q(full_name__icontains=search_query)
        )

    # --- Lọc theo khoa/phòng ---
    if department_id:
        employees = employees.filter(department_id=department_id)

    # --- Lọc theo chức danh nghề nghiệp ---
    if job_title:
        employees = employees.filter(job_title__icontains=job_title)

    # --- Sắp xếp ---
    if sort == "code":
        employees = employees.order_by("code" if direction == "asc" else "-code")
    elif sort == "full_name":
        employees = employees.order_by("full_name" if direction == "asc" else "-full_name")
    elif sort == "department":
        employees = employees.order_by("department__name" if direction == "asc" else "-department__name")

    departments = Department.objects.all().order_by("name")
    job_titles = Employee.objects.values_list("job_title", flat=True).distinct().exclude(job_title__exact="")

    context = {
        "employees": employees,
        "departments": departments,
        "job_titles": job_titles,
        "search_query": search_query,
        "selected_department": department_id,
        "selected_job_title": job_title,
        "sort": sort,
        "dir": direction,
    }
    return render(request, "health_records/employee_list.html", context)



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
    # Base queryset
    qs = HealthRecord.objects.select_related(
        'employee', 'employee__department', 'health_classification'
    ).all().order_by('-exam_date', '-id')

    # ----- READ FILTERS -----
    q = (request.GET.get('q') or '').strip()
    year = (request.GET.get('year') or '').strip()
    classification = (request.GET.get('classification') or request.GET.get('filter_hc') or '').strip()
    conclusion = (request.GET.get('conclusion') or request.GET.get('filter_conclusion') or '').strip()
    vaccinated = (request.GET.get('vaccinated') or '').strip()

    # ----- APPLY FILTERS -----
    if q:
        qs = qs.filter(
            Q(employee__code__icontains=q) |
            Q(employee__full_name__icontains=q)
        )

    if year:
        try:
            qs = qs.filter(year=int(year))
        except:
            pass

    # Phân loại (support id or name)
    if classification:
        try:
            cid = int(classification)
            qs = qs.filter(health_classification_id=cid)
        except:
            qs = qs.filter(
                Q(health_classification__name__icontains=classification)
            )

    # Kết luận
    if conclusion:
        qs = qs.filter(conclusion_text__icontains=conclusion.strip())

    # Vaccine
    if vaccinated != '':
        if vaccinated.lower() in ['1','yes','y','true','đã','co','có']:
            qs = qs.filter(vaccinated=True)
        elif vaccinated.lower() in ['0','no','n','false','chưa']:
            qs = qs.filter(vaccinated=False)

    # ----- PAGINATION -----
    paginator = Paginator(qs, 15)
    page_param = request.GET.get('page')

    try:
        page_number = int(page_param) if page_param else 1
    except:
        page_number = 1

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # ----- QUERYSTRING (KEEP FILTERS FOR PAGINATION) -----
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    querystring = urlencode({k: v for k, v in params.items() if v != ''})

    # ----- EXTRA LISTS FOR TEMPLATE -----
    years = HealthRecord.objects.order_by('-year').values_list('year', flat=True).distinct()
    health_classes = HealthClassification.objects.all()
    raw_conclusions = HealthRecord.objects \
    .exclude(conclusion_text__isnull=True) \
    .exclude(conclusion_text__exact='') \
    .values_list('conclusion_text', flat=True)

    # normalize: strip and remove empty, preserve order and dedupe
    normalized = []
    for c in raw_conclusions:
        try:
            s = str(c).strip()
        except:
            s = None
        if s:
            normalized.append(s)

    # dedupe preserving order
    conclusions = list(dict.fromkeys(normalized))

    # ----- CONTEXT -----
    context = {
        'page_obj': page_obj,
        'records': page_obj.object_list,
        'paginator': paginator,
        'querystring': querystring,

        # Current filters
        'filter_q': q,
        'filter_year': year,
        'filter_hc': classification,
        'filter_conclusion': conclusion,
        'filter_vaccinated': vaccinated,

        # Data for dropdowns
        'years': years,
        'health_classes': health_classes,
        'conclusions': conclusions,
    }

    return render(request, 'health_records/healthrecord_list.html', context)


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
        try:
            df = pd.read_excel(file)
        except Exception as e:
            messages.error(request, f"Lỗi đọc file Excel: {e}")
            return redirect('healthrecord_import')

        missing_employees = []
        created_count = 0
        for idx, row in df.iterrows():
            emp_code = str(row.get('Mã nhân viên') or '').strip()
            if not emp_code:
                missing_employees.append(f'(dòng {idx+2}: thiếu mã)')
                continue
            try:
                employee = Employee.objects.get(code=emp_code)
            except Employee.DoesNotExist:
                missing_employees.append(emp_code)
                continue

            examination_type = ExaminationType.objects.filter(name=row.get('Loại khám')).first()
            classification = HealthClassification.objects.filter(name=row.get('Phân loại sức khoẻ')).first()

            # parse boolean vaccinated
            vaccinated_raw = row.get('Đã tiêm vắc-xin')
            vaccinated = False
            if pd.notna(vaccinated_raw):
                if str(vaccinated_raw).strip().lower() in ['x','có','co','yes','1','true']:
                    vaccinated = True

            # parse dates safely
            exam_date = row.get('Ngày khám')
            vac_date = row.get('Ngày tiêm chủng') or row.get('vaccination_date') or None

            try:
                rec, created = HealthRecord.objects.update_or_create(
                    employee=employee,
                    year=int(row.get('Năm khám')),
                    defaults={
                        'exam_date': exam_date if not pd.isna(exam_date) else None,
                        'examination_type': examination_type,
                        'clinic_name': row.get('Cơ sở khám'),
                        'height_cm': row.get('Chiều cao (cm)') if not pd.isna(row.get('Chiều cao (cm)')) else None,
                        'weight_kg': row.get('Cân nặng (kg)') if not pd.isna(row.get('Cân nặng (kg)')) else None,
                        'blood_pressure': row.get('Huyết áp (mmHg)'),
                        'health_classification': classification,
                        'conclusion_text': row.get('Kết luận (nếu muốn nhập tay)'),
                        'vaccinated': vaccinated,
                        'vaccine_name': row.get('Tên vắc-xin'),
                        'vaccination_date': vac_date if (pd.notna(vac_date) if pd.notna(vac_date) else False) else None,
                        'note': row.get('Ghi chú'),
                    }
                )
                if created:
                    created_count += 1
            except Exception as e:
                # log but continue
                traceback.print_exc()
                missing_employees.append(f"{emp_code} (lỗi: {e})")

        if missing_employees:
            messages.warning(request, f"Một số mã nhân viên không tồn tại hoặc lỗi: {', '.join(map(str, missing_employees)[:30])}")
        if created_count:
            messages.success(request, f"Đã tạo/ cập nhật {created_count} hồ sơ.")
        return redirect('healthrecord_list')

    return render(request, 'health_records/healthrecord_import.html', {'title': 'Import hồ sơ sức khỏe từ Excel'})

def download_sample_healthrecord(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'samples', 'mau_import_hssk.xlsx')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='mau_import_hssk.xlsx')

# ------------------------
# export health records (xlsx) theo filter hiện hành
# ------------------------
def export_healthrecords_xlsx(request):
    qs = HealthRecord.objects.select_related('employee', 'employee__department', 'health_classification')

    # áp cùng filter như list
    q = request.GET.get('q', '').strip()
    year = request.GET.get('year', '').strip()
    dept_id = request.GET.get('department', '').strip()
    hc_id = request.GET.get('health_classification', '').strip()
    status = request.GET.get('status', '').strip()

    if q:
        qs = qs.filter(Q(employee__code__icontains=q) | Q(employee__full_name__icontains=q))
    if year:
        try:
            year_int = int(year)
            qs = qs.filter(year=year_int)
        except:
            pass
    if dept_id:
        qs = qs.filter(employee__department_id=dept_id)
    if hc_id:
        qs = qs.filter(health_classification_id=hc_id)
    if status:
        qs = qs.filter(status=status)

    # tạo DataFrame
    rows = []
    for r in qs.order_by('-year', 'employee__full_name'):
        rows.append({
            'Mã nhân viên': r.employee.code,
            'Họ và tên': r.employee.full_name,
            'Khoa/Phòng': r.employee.department.name if r.employee.department else '',
            'Năm khám': r.year,
            'Ngày khám': r.exam_date,
            'Loại khám': r.examination_type.name if r.examination_type else '',
            'Cơ sở khám': r.clinic_name or '',
            'Chiều cao (cm)': r.height_cm,
            'Cân nặng (kg)': r.weight_kg,
            'Huyết áp (mmHg)': r.blood_pressure,
            'Phân loại sức khỏe': r.health_classification.name if r.health_classification else '',
            'Kết luận': r.conclusion,
            'Đã tiêm vắc-xin': 'Có' if r.vaccinated else 'Không',
            'Tên vắc-xin': r.vaccine_name or '',
            'Ngày tiêm': r.vaccination_date,
            'Trạng thái': r.status,
            'Ghi chú': r.note or '',
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='HealthRecords')
    output.seek(0)
    filename = f"health_records_{datetime.date.today().isoformat()}.xlsx"
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# 1) AJAX preview import (tạo batch + lưu HealthRecordTemp)
def parse_date_cell(raw):
    """Trả về datetime.date hoặc None. Hỗ trợ pd.Timestamp, Excel serial, và nhiều format string."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    if isinstance(raw, (pd.Timestamp, datetime)):
        try:
            return raw.date()
        except:
            pass
    try:
        ts = pd.to_datetime(raw, errors='coerce', dayfirst=True)
        if pd.notna(ts):
            return ts.date()
    except:
        pass
    s = str(raw).strip()
    # remove surrounding quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    # normalize separators
    s2 = re.sub(r'[.\-]', '/', s)
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(s2, fmt).date()
        except:
            pass
    return None

# ---- helper: find best matching column name in df ----
def find_column(df, candidates):
    cols = list(df.columns)
    # exact
    for c in candidates:
        if c in cols:
            return c
    # case-insensitive direct
    lc = {col.lower().strip(): col for col in cols}
    for c in candidates:
        key = c.lower().strip()
        if key in lc:
            return lc[key]
    # substring match (normalize spaces)
    cols_norm = {col.replace(" ", "").lower(): col for col in cols}
    for c in candidates:
        k = c.replace(" ", "").lower()
        for kn, orig in cols_norm.items():
            if k in kn or kn in k:
                return orig
    return None

# ------------------------------
# Preview import (AJAX) - single-column vaccine
# ------------------------------
def healthrecord_import_preview_ajax(request):
    """
    Preview import hồ sơ sức khỏe — báo lỗi chi tiết giống employee_import_preview_ajax.
    """
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            df = pd.read_excel(file, engine='openpyxl')
            batch_id = str(uuid.uuid4())[:8]

            # Xoá batch tạm cùng batch_id trước (an toàn hơn là xóa tất cả)
            HealthRecordTemp.objects.filter(batch_id=batch_id).delete()
            temp_objects = []

            for _, row in df.iterrows():
                # --- đọc các cột phổ biến (chỉnh nếu file header khác) ---
                code = row.get('Mã nhân viên') if 'Mã nhân viên' in df.columns else row.get('Mã NV') if 'Mã NV' in df.columns else row.get('Ma nhan vien') if 'Ma nhan vien' in df.columns else None
                full_name = row.get('Họ và tên') if 'Họ và tên' in df.columns else row.get('Ho va ten') if 'Ho va ten' in df.columns else None
                year_raw = row.get('Năm khám') if 'Năm khám' in df.columns else None
                raw_exam_date = row.get('Ngày khám') if 'Ngày khám' in df.columns else None
                exam_type_raw = row.get('Loại khám') if 'Loại khám' in df.columns else None
                clinic_raw = row.get('Cơ sở khám') if 'Cơ sở khám' in df.columns else None
                height_raw = row.get('Chiều cao (cm)') if 'Chiều cao (cm)' in df.columns else None
                weight_raw = row.get('Cân nặng (kg)') if 'Cân nặng (kg)' in df.columns else None
                bp_raw = row.get('Huyết áp (mmHg)') if 'Huyết áp (mmHg)' in df.columns else None
                health_raw = row.get('Phân loại sức khoẻ') if 'Phân loại sức khoẻ' in df.columns else None
                conclusion_raw = row.get('Kết luận (nếu muốn nhập tay)') if 'Kết luận (nếu muốn nhập tay)' in df.columns else None
                vaccine_cell = row.get('Đã tiêm vắc-xin') if 'Đã tiêm vắc-xin' in df.columns else None
                raw_vac_date = row.get('Ngày tiêm chủng') if 'Ngày tiêm chủng' in df.columns else None
                note_raw = row.get('Ghi chú') if 'Ghi chú' in df.columns else None

                # normalize
                if pd.isna(code): code = None
                if pd.isna(full_name): full_name = None
                if pd.isna(year_raw): year_raw = None
                if pd.isna(raw_exam_date): raw_exam_date = None
                if pd.isna(exam_type_raw): exam_type_raw = None
                if pd.isna(clinic_raw): clinic_raw = None
                if pd.isna(height_raw): height_raw = None
                if pd.isna(weight_raw): weight_raw = None
                if pd.isna(bp_raw): bp_raw = None
                if pd.isna(health_raw): health_raw = None
                if pd.isna(conclusion_raw): conclusion_raw = None
                if pd.isna(vaccine_cell): vaccine_cell = None
                if pd.isna(raw_vac_date): raw_vac_date = None
                if pd.isna(note_raw): note_raw = None

                # VALIDATION & PARSE
                is_valid = True
                error_message = None

                # mã NV bắt buộc
                code_clean = str(code).strip() if code else None
                if not code_clean:
                    is_valid = False
                    error_message = "Thiếu Mã nhân viên"

                # kiểm tra tồn tại Employee
                emp_obj = None
                if code_clean:
                    emp_obj = Employee.objects.filter(code__iexact=code_clean).first()
                    if not emp_obj:
                        is_valid = False
                        error_message = (error_message or "") + ("; Mã nhân viên không tồn tại")

                # parse ngày khám
                exam_date_parsed = None
                if raw_exam_date is not None and str(raw_exam_date).strip() != '':
                    exam_date_parsed = parse_date_cell(raw_exam_date)
                    if exam_date_parsed is None:
                        is_valid = False
                        error_message = (error_message or "") + ("; Ngày khám không hợp lệ")

                # parse ngày tiêm
                vac_date_parsed = None
                if raw_vac_date is not None and str(raw_vac_date).strip() != '':
                    vac_date_parsed = parse_date_cell(raw_vac_date)
                    if vac_date_parsed is None:
                        is_valid = False
                        error_message = (error_message or "") + ("; Ngày tiêm không hợp lệ")

                # parse numeric height/weight
                height_val = None
                weight_val = None
                try:
                    if height_raw is not None and str(height_raw).strip() != '':
                        height_val = float(str(height_raw).replace(',', '.').replace('cm','').strip())
                except:
                    is_valid = False
                    error_message = (error_message or "") + ("; Chiều cao không đúng định dạng")
                try:
                    if weight_raw is not None and str(weight_raw).strip() != '':
                        weight_val = float(str(weight_raw).replace(',', '.').replace('kg','').strip())
                except:
                    is_valid = False
                    error_message = (error_message or "") + ("; Cân nặng không đúng định dạng")

                # phân loại sức khỏe: kiểm tra trong danh mục (nếu bạn muốn bắt buộc)
                hc_obj = None
                if health_raw:
                    hc_obj = HealthClassification.objects.filter(name__iexact=str(health_raw).strip()).first()
                    if not hc_obj:
                        # chỉ cảnh báo (không bắt buộc) -> ghi vào error_message để bạn thấy
                        error_message = (error_message or "") + ("; Phân loại sức khoẻ chưa có trong danh mục")

                # vaccine single-column logic (nếu tên vắc-xin có trong ô => vaccinated True)
                vaccinated_flag = False
                vaccine_name_value = None
                if vaccine_cell and str(vaccine_cell).strip():
                    s = str(vaccine_cell).strip()
                    parts = [p.strip() for p in re.split(r'[;,]', s) if p.strip()]
                    if parts:
                        vaccine_name_value = '; '.join(parts)
                        vaccinated_flag = True
                # infer vaccinated from vac_date if name absent
                if not vaccinated_flag and raw_vac_date and vac_date_parsed:
                    vaccinated_flag = True

                # tạo object tạm (trùng tên field với model HealthRecordTemp)
                temp_objects.append(HealthRecordTemp(
                    batch_id=batch_id,
                    employee_code=code_clean,
                    employee_name=(emp_obj.full_name if emp_obj else (str(full_name).strip() if full_name else None)),
                    year=(int(year_raw) if (year_raw is not None and str(year_raw).strip().isdigit()) else (exam_date_parsed.year if exam_date_parsed else None)),
                    exam_date=exam_date_parsed,
                    examination_type_name=(str(exam_type_raw).strip() if exam_type_raw else None),
                    clinic_name=(str(clinic_raw).strip() if clinic_raw else None),
                    height_cm=height_val,
                    weight_kg=weight_val,
                    blood_pressure=(str(bp_raw).strip() if bp_raw else None),
                    health_classification_name=(str(health_raw).strip() if health_raw else None),
                    conclusion_text=(str(conclusion_raw).strip() if conclusion_raw else None),
                    vaccinated=bool(vaccinated_flag),
                    vaccine_name=(vaccine_name_value if vaccinated_flag and vaccine_name_value else None),
                    vaccination_date=vac_date_parsed,
                    note=(str(note_raw).strip() if note_raw else None),
                    is_valid=is_valid,
                    error_message=(error_message.strip(' ;') if error_message else None),
                ))

            # lưu tạm và render partial preview
            HealthRecordTemp.objects.bulk_create(temp_objects)
            temps = HealthRecordTemp.objects.filter(batch_id=batch_id).order_by('employee_code')

            total = temps.count()
            valid_count = temps.filter(is_valid=True).count()
            invalid_count = temps.filter(is_valid=False).count()
            all_valid = invalid_count == 0

            html = render_to_string('health_records/_healthrecord_preview_table.html', {
                'temps': temps,
                'batch_id': batch_id,
                'total': total,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'all_valid': all_valid,
            })

            return JsonResponse({'html': html})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': f"Lỗi xử lý file: {e}"}, status=500)

    return JsonResponse({'error': 'Không có file được tải lên.'}, status=400)

# ------------------------------
# Submit batch (AJAX) — lưu HealthRecord từ HealthRecordTemp
# ------------------------------
@transaction.atomic
def healthrecord_import_submit_ajax(request, batch_id):
    if request.method != 'POST':
        return JsonResponse({'error':'Phải gọi POST'}, status=405)
    try:
        temps = HealthRecordTemp.objects.filter(batch_id=batch_id, is_valid=True)
        if not temps.exists():
            return JsonResponse({'error':'Không có dữ liệu hợp lệ để lưu.'}, status=400)

        created = 0
        for t in temps:
            try:
                emp = Employee.objects.get(code__iexact=t.employee_code)
            except Employee.DoesNotExist:
                continue

            exam_type = ExaminationType.objects.filter(name__iexact=(t.examination_type_name or "").strip()).first()
            hc = HealthClassification.objects.filter(name__iexact=(t.health_classification_name or "").strip()).first()

            rec, was_created = HealthRecord.objects.update_or_create(
                employee=emp,
                year=t.year or (t.exam_date.year if t.exam_date else timezone.now().year),
                defaults={
                    'exam_date': t.exam_date,
                    'examination_type': exam_type,
                    'clinic_name': t.clinic_name,
                    'height_cm': t.height_cm,
                    'weight_kg': t.weight_kg,
                    'blood_pressure': t.blood_pressure,
                    'health_classification': hc,
                    'conclusion_text': t.conclusion_text,
                    'vaccinated': t.vaccinated,
                    'vaccine_name': t.vaccine_name if t.vaccinated else None,
                    'vaccination_date': t.vaccination_date,
                    'note': t.note,
                }
            )
            if was_created:
                created += 1

        HealthRecordTemp.objects.filter(batch_id=batch_id).delete()
        return JsonResponse({'success': True, 'created': created})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Lỗi khi lưu: {e}'}, status=500)

# ------------------------------
# Cancel batch (AJAX)
# ------------------------------
def healthrecord_import_cancel_ajax(request, batch_id):
    if request.method not in ('POST','GET'):
        return JsonResponse({'error':'Method not allowed'}, status=405)
    HealthRecordTemp.objects.filter(batch_id=batch_id).delete()
    return JsonResponse({'success': True})
# ----------------- END: Paste-ready block -----------------


# ========== IMPORT NHÂN VIÊN ==========

# Trang hiển thị giao diện import (form + preview-container)
def employee_import(request):
    """Hiển thị trang form import nhân viên (nơi chạy AJAX preview)."""
    return render(request, 'health_records/employee_import.html', {
        'title': 'Import danh sách nhân viên'
    })

# 1️⃣ AJAX import preview (có log lỗi chi tiết)
def employee_import_preview_ajax(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            df = pd.read_excel(file)
            batch_id = str(uuid.uuid4())[:8]

            EmployeeTemp.objects.all().delete()
            temp_objects = []

            for _, row in df.iterrows():
                code = row.get('Mã nhân viên')
                full_name = row.get('Họ và tên')
                dept_name = row.get('Khoa/Phòng')
                gender = row.get('Giới tính')
                job_title = row.get('Chức danh nghề nghiệp')
                position = row.get('Chức vụ')
                birth_year = row.get('Năm sinh')

                if pd.isna(code): code = None
                if pd.isna(full_name): full_name = None
                if pd.isna(dept_name): dept_name = None
                if pd.isna(gender): gender = None
                if pd.isna(job_title): job_title = None
                if pd.isna(position): position = None
                if pd.isna(birth_year): birth_year = None

                is_valid = True
                error_message = None

                if not code or not full_name:
                    is_valid = False
                    error_message = "Thiếu mã nhân viên hoặc họ tên"
                else:
                    if dept_name:
                        dept = Department.objects.filter(name__iexact=dept_name.strip()).first()
                        if not dept:
                            is_valid = False
                            error_message = f"Khoa/Phòng '{dept_name}' chưa tồn tại"

                temp_objects.append(EmployeeTemp(
                    batch_id=batch_id,
                    code=str(code).strip() if code else None,
                    full_name=str(full_name).strip() if full_name else None,
                    birth_year=int(birth_year) if birth_year else None,
                    gender=str(gender).capitalize() if gender else None,
                    job_title=job_title,
                    position=position,
                    department_name=dept_name,
                    is_valid=is_valid,
                    error_message=error_message,
                ))

            EmployeeTemp.objects.bulk_create(temp_objects)
            temps = EmployeeTemp.objects.filter(batch_id=batch_id).order_by('code')

            total = temps.count()
            valid_count = temps.filter(is_valid=True).count()
            invalid_count = temps.filter(is_valid=False).count()
            all_valid = invalid_count == 0

            html = render_to_string('health_records/_employee_preview_table.html', {
                'temps': temps,
                'batch_id': batch_id,
                'total': total,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'all_valid': all_valid,
            })

            return JsonResponse({'html': html})
        except Exception as e:
            return JsonResponse({'error': f"Lỗi xử lý file: {e}"}, status=500)

    return JsonResponse({'error': 'Không có file được tải lên.'}, status=400)

# 2️⃣ Lưu chính thức
@transaction.atomic
def employee_import_submit_ajax(request, batch_id):
    try:
        temps = EmployeeTemp.objects.filter(batch_id=batch_id, is_valid=True)
        if not temps.exists():
            return JsonResponse({'error': 'Không có dữ liệu hợp lệ để lưu.'}, status=400)

        for temp in temps:
            dept_name = (temp.department_name or "").strip()
            dept = Department.objects.filter(name__iexact=dept_name).first() if dept_name else None

            Employee.objects.update_or_create(
                code=str(temp.code).strip(),
                defaults={
                    'full_name': (temp.full_name or "").strip(),
                    'birth_year': temp.birth_year or None,
                    'gender': temp.gender or None,
                    'job_title': temp.job_title or "",
                    'position': temp.position or "",
                    'department': dept,
                }
            )

        # Dọn batch tạm sau khi lưu xong
        EmployeeTemp.objects.filter(batch_id=batch_id).delete()
        return JsonResponse({'success': True})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Lỗi khi lưu dữ liệu: {e}'}, status=500)


# 3️⃣ Huỷ batch
def employee_import_cancel_ajax(request, batch_id):
    EmployeeTemp.objects.filter(batch_id=batch_id).delete()
    return JsonResponse({'success': True})


def download_sample_employee(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'samples', 'mau_import_nv.xlsx')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='mau_import_nv.xlsx')

