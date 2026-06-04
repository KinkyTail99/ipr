from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['last_name', 'first_name', 'patronymic', 'phone', 'birth_date', 'has_child', 'comment']
        widgets = {
            'last_name': forms.TextInput(attrs={'style': 'padding: 10px; width: 100%; border: 1px solid #ccc; margin-bottom: 15px;'}),
            'first_name': forms.TextInput(attrs={'style': 'padding: 10px; width: 100%; border: 1px solid #ccc; margin-bottom: 15px;'}),
            'patronymic': forms.TextInput(attrs={'style': 'padding: 10px; width: 100%; border: 1px solid #ccc; margin-bottom: 15px;'}),
            'phone': forms.TextInput(attrs={'placeholder': '+375 (29) XXX-XX-XX', 'style': 'padding: 10px; width: 100%; border: 1px solid #ccc; margin-bottom: 15px;'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'style': 'padding: 10px; width: 100%; border: 1px solid #ccc; margin-bottom: 15px;'}),
            'has_child': forms.CheckboxInput(attrs={'style': 'margin-bottom: 15px;'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'style': 'padding: 10px; width: 100%; border: 1px solid #ccc; margin-bottom: 15px;'}),
        }
