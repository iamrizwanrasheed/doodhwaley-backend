from django import forms
from milkapp.models import Customer,Area,SubArea,User,City

class CustomerForm(forms.ModelForm):
    city = forms.ModelChoiceField(queryset=City.objects.all())
    area = forms.ModelChoiceField(queryset=Area.objects.all())
    subarea = forms.ModelChoiceField(queryset=SubArea.objects.all())
    class Meta:
        model = User
        fields = ['username','email','password','image','city','area','subarea']
    


