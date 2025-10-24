from django import forms
from .models import HealthRecord, Employee, Department, ExaminationType, HealthClassification


class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = [
            "employee", "year", "exam_date", "examination_type", "clinic_name",
            "height_cm", "weight_kg", "blood_pressure",
            "vaccinated", "vaccine_name", "vaccination_date",
            "health_classification", "conclusion_text",
            "result_file", "note", "status"
        ]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-select"}),
            "year": forms.NumberInput(attrs={"class": "form-control", "placeholder": "VD: 2025"}),
            "exam_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "examination_type": forms.Select(attrs={"class": "form-select"}),
            "clinic_name": forms.TextInput(attrs={"class": "form-control"}),
            "height_cm": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "weight_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "blood_pressure": forms.TextInput(attrs={"class": "form-control", "placeholder": "VD: 120/80"}),
            "vaccinated": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "vaccine_name": forms.TextInput(attrs={"class": "form-control"}),
            "vaccination_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "health_classification": forms.Select(attrs={"class": "form-select"}),
            "conclusion_text": forms.TextInput(attrs={"class": "form-control"}),
            "result_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
