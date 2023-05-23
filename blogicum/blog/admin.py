from django.contrib import admin

from .models import Post, Category, Location, Comment, Profile

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'pub_date',
        'author',
        'location',
        'category'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Comment)
admin.site.register(Profile)
