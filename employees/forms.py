from django import forms

from .models import Employee, Payroll


class PayrollForm(forms.ModelForm):
    pay_period = forms.DateField(
        input_formats=['%Y-%m'],
        widget=forms.DateInput(format='%Y-%m', attrs={'type': 'month'}),
    )

    class Meta:
        model = Payroll
        fields = (
            'employee',
            'pay_period',
            'gross_pay',
            'deductions',
            'status',
            'payment_date',
        )
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'gross_pay': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.order_by('first_name', 'last_name')
        self.fields['pay_period'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        pay_period = cleaned_data.get('pay_period')
        if pay_period:
            cleaned_data['pay_period'] = pay_period.replace(day=1)
            self.instance.pay_period = cleaned_data['pay_period']
        return cleaned_data
