from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class AdminPost(admin.ModelAdmin):
    list_display = ['title', 'publish', 'author', 'status']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'body']
    raw_id_fields = ('author',)
    ordering = ['status', 'publish']
    list_filter = ('status', 'created', 'publish', 'author',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
