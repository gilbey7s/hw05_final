from django.contrib import admin

from .models import Group, Post, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "text",
        "pub_date",
        "author",
        "group",
    )
    search_fields = ("text",)
    list_filter = ("pub_date",)
    list_editable = ("group",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "post",
        "author",
        "text",
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "author",
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
