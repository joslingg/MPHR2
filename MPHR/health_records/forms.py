from django import forms
from .models import HealthRecord

# 1️⃣ Form nhập thông tin hồ sơ sức khỏe
class HealthRecordForm(forms.ModelForm):

    # 4️⃣ Cấu hình form (fields, widget, label)
    class Meta:
        model = HealthRecord
        fields = [
            "ma_nv", "full_name", "birth_year", "gender",
            "job_title", "position", "department",
            "vaccinated_influvac", "vaccinated_vaxigrip", "vaccination_date",
            "year", "exam_date", "exam_type", "clinic_name",
            "height_cm", "weight_kg", "blood_pressure",
            "health_classification", "conclusion_text",
            "group", "note", "result_file",
        ]
        widgets = {
            "ma_nv": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nhập mã nhân viên"
            }),
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nhập họ và tên"
            }),
            "birth_year": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Ví dụ: 1985"
            }),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "job_title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "VD: Điều dưỡng, Bác sĩ, Hộ lý..."
            }),
            "position": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "VD: Trưởng khoa, Nhân viên..."
            }),
            "department": forms.Select(attrs={"class": "form-select"}),
            "vaccinated_influvac": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "vaccinated_vaxigrip": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "vaccination_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "year": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Nhập năm khám"
            }),
            "exam_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "exam_type": forms.Select(attrs={"class": "form-select"}),
            "clinic_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nhập tên cơ sở khám"
            }),
            "height_cm": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "VD: 160"
            }),
            "weight_kg": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "VD: 52"
            }),
            "blood_pressure": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "VD: 120/80"
            }),
            "health_classification": forms.Select(attrs={"class": "form-select"}),
            "conclusion_text": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nhập kết luận nếu có"
            }),
            "group": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "VD: Nhóm 1, Nhóm 2..."
            }),
            "note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ghi chú thêm (nếu có)"
            }),
            "result_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "ma_nv": "Mã nhân viên",
            "full_name": "Họ và tên",
            "birth_year": "Năm sinh",
            "gender": "Giới tính",
            "job_title": "Chức danh nghề nghiệp",
            "position": "Chức vụ",
            "department": "Khoa/Phòng",
            "vaccinated_influvac": "Đã tiêm Influvac (Hà Lan)",
            "vaccinated_vaxigrip": "Đã tiêm Vaxigrip (Pháp)",
            "vaccination_date": "Ngày tiêm chủng",
            "year": "Năm khám",
            "exam_date": "Ngày khám",
            "exam_type": "Loại khám",
            "clinic_name": "Cơ sở khám",
            "height_cm": "Chiều cao (cm)",
            "weight_kg": "Cân nặng (kg)",
            "blood_pressure": "Huyết áp (mmHg)",
            "health_classification": "Phân loại sức khoẻ",
            "conclusion_text": "Kết luận (nếu muốn nhập tay)",
            "group": "Nhóm",
            "note": "Ghi chú",
            "result_file": "File kết quả (PDF)",
        }

    # 3️⃣ Kiểm tra logic hợp lệ khi nhập form
    def clean(self):
        cleaned_data = super().clean()
        vaccinated_influvac = cleaned_data.get("vaccinated_influvac")
        vaccinated_vaxigrip = cleaned_data.get("vaccinated_vaxigrip")
        vaccination_date = cleaned_data.get("vaccination_date")

        if vaccination_date and not (vaccinated_influvac or vaccinated_vaxigrip):
            raise forms.ValidationError("Bạn đã nhập ngày tiêm nhưng chưa chọn loại vacxin.")
        return cleaned_data


# 2️⃣ Form import file Excel
class ExcelImportForm(forms.Form):
    file = forms.FileField(
        label="Chọn file Excel (.xlsx)",
        allow_empty_file=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": ".xlsx"
        })
    )
