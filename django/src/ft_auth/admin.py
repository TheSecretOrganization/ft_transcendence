from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import User, FtOauth

class UserCreationForm(forms.ModelForm):
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ['username', 'is_admin']

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise ValidationError('Passwords doesn\'t match')
		return password2

	def save(self, commit=True):
		user = super().save(commit=False)
		user.set_password(self.cleaned_data['password1'])
		if commit:
			user.save()
		return user

class UserChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField

	class Meta:
		model = User
		fields = ['username', 'password', 'is_admin', 'is_active']

class UserAdmin(BaseUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ['username', 'is_active', 'is_admin']
	list_filter = ['is_active', 'is_admin']
	fieldsets = [
		(None, {'fields': ['username', 'password', 'is_active']}),
		('Permissions', {'fields': ['is_admin']}),
	]
	add_fieldsets = [
		(
			None,
			{
				'classes': ['wide'],
				'fields': ['username', 'password1', 'password2', 'is_admin'],
			},
		),
	]
	search_fields = ['username']
	ordering = ['username']
	filter_horizontal = []

admin.site.register(User, UserAdmin)
admin.site.register(FtOauth)
admin.site.unregister(Group)
