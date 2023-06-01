from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment


User = get_user_model()


class PostForm2(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        exclude = ['author']
        widgets = {
            'post': forms.DateInput(attrs={'type': 'date'}),
        }


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category')
        widgets = {
            'post': forms.DateInput(attrs={'type': 'date'}),
        }


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'rows': '4',
    }))

    class Meta:
        model = Comment
        fields = ('text',)

        def __init__(self, *args, **kwargs):
            self.user = kwargs.pop('user', None)
            super(CommentForm, self).__init__(*args, **kwargs)

        def save(self, commit=True):
            obj = super(CommentForm, self).save(commit=False)
            obj.user = self.user
            if commit:
                obj.save()
            return obj


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
