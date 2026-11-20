from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


User = get_user_model()


class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Foydalanuvchi nomi yoki parol noto‘g‘ri.',
        'inactive': 'Bu hisob faol emas.',
    }
    username = forms.CharField(
        label='Foydalanuvchi nomi',
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'autocomplete': 'username',
            'placeholder': 'Foydalanuvchi nomini kiriting',
        }),
    )
    password = forms.CharField(
        label='Parol',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Parolingizni kiriting',
        }),
    )


class RegistrationForm(UserCreationForm):
    error_messages = {
        **UserCreationForm.error_messages,
        'password_mismatch': 'Kiritilgan parollar bir-biriga mos kelmadi.',
    }
    email = forms.EmailField(
        label='Elektron pochta',
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'siz@example.com'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
        labels = {'username': 'Foydalanuvchi nomi'}
        widgets = {
            'username': forms.TextInput(attrs={
                'autocomplete': 'username',
                'placeholder': 'Foydalanuvchi nomini kiriting',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = (
            '150 belgigacha: harf, raqam va @/./+/-/_ belgilaridan foydalaning.'
        )
        self.fields['password1'].label = 'Parol'
        self.fields['password1'].help_text = (
            'Kamida 8 ta belgi kiriting; keng tarqalgan yoki faqat raqamli parol tanlamang.'
        )
        self.fields['password1'].widget.attrs.update({
            'autocomplete': 'new-password',
            'placeholder': 'Kamida 8 ta belgidan iborat parol',
        })
        self.fields['password2'].label = 'Parolni tasdiqlang'
        self.fields['password2'].help_text = ''
        self.fields['password2'].widget.attrs.update({
            'autocomplete': 'new-password',
            'placeholder': 'Parolni qayta kiriting',
        })

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Bu elektron pochta manzili bilan hisob mavjud.')
        return email
