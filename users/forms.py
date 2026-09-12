from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Profile

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={
        'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700/60 rounded-xl text-white focus:outline-none focus:border-cyan-500'
    }))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field != self.fields['role']:
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700/60 rounded-xl text-white focus:outline-none focus:border-cyan-500 placeholder-slate-500'
                })

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('title', 'bio', 'hourly_rate', 'skills', 'company_name', 'website')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700/60 rounded-xl text-white focus:outline-none focus:border-cyan-500 placeholder-slate-500'
            })

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'location', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field != self.fields['avatar']:
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700/60 rounded-xl text-white focus:outline-none focus:border-cyan-500 placeholder-slate-500'
                })
