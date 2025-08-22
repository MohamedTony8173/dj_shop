from django import forms 
from .models import AccountNew, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password'}), required=True)
    
    class Meta:
        model = AccountNew
        fields = ['username','email','phone_number']
    
    def clean(self):
        super(RegistrationForm,self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError('password does not match!')
            
        
        
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm,self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Enter User Name'
        self.fields['email'].widget.attrs['placeholder'] = 'your@example.com'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
    
    
    
class UserForm(forms.ModelForm):
    class Meta:
        model = AccountNew
        fields = ['username','phone_number']    
    def __init__(self,*args, **kwargs):
        super(UserForm,self).__init__(*args, **kwargs) 
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'   
        
        
            
class ProfileUserForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False,error_messages={'invalid':('just image is allowed',)},widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line_1','address_line_2','city','state','profile_pic'] 
        
    def __init__(self,*args, **kwargs):
        super(ProfileUserForm,self).__init__(*args, **kwargs) 
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
              