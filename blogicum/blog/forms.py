from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'image', 'location', 'category')
        widgets = {
            'post': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'format': '%m/%d/%y %H:%M'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(PostForm, self).save(commit=False)
        obj.user = self.user
        if commit:
            obj.save()
        return obj


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
