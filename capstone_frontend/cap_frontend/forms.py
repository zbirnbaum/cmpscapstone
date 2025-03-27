from django import forms
from .models import Photos


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photos
        fields = [ 'location', 'comment', 'image']  # Ensure these match your model

    image = forms.ImageField(label='Tree Photo')  # Optional: Customize the image field label
