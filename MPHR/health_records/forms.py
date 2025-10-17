from django import forms
from .models import HealthRecord


class HealthRecordForm(forms.ModelForm):
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
            "ma_nv": forms.TextInput(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "birth_year": forms.NumberInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "vaccinated_influvac": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "vaccinated_vaxigrip": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "vaccination_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "year": forms.NumberInput(attrs={"class": "form-control"}),
            "exam_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "exam_type": forms.Select(attrs={"class": "form-select"}),
            "clinic_name": forms.TextInput(attrs={"class": "form-control"}),
            "height_cm": forms.NumberInput(attrs={"class": "form-control"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control"}),
            "blood_pressure": forms.TextInput(attrs={"class": "form-control"}),
            "health_classification": forms.Select(attrs={"class": "form-select"}),
            "conclusion_text": forms.TextInput(attrs={"class": "form-control"}),
            "group": forms.TextInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
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

    def clean(self):
        cleaned_data = super().clean()
        vaccinated_influvac = cleaned_data.get("vaccinated_influvac")
        vaccinated_vaxigrip = cleaned_data.get("vaccinated_vaxigrip")
        vaccination_date = cleaned_data.get("vaccination_date")

        if vaccination_date and not (vaccinated_influvac or vaccinated_vaxigrip):
            raise forms.ValidationError("Bạn đã nhập ngày tiêm nhưng chưa chọn loại vacxin.")
        return cleaned_data
