from django import forms


class PermissionSlipFormParent(forms.Form):
    name = forms.CharField(required=True, label='Enter your name.')
    electronic_consent = forms.BooleanField(required=True, label='By checking this box you consent to electronically signing this document.')


class PermissionSlipFormStudent(forms.Form):
    name = forms.CharField(required=True, label='Enter your name.')
    electronic_consent = forms.BooleanField(required=True, label='By checking this box you signal that you have read and understand that the school handbook rules are in effect during this field trip.')
