from django.contrib import admin

from .models import (Article, Author, Category, Comment, Content, Hotags,
                     Hotarticle, Review, SubscriptionPlan, Subscriptions, User,
                     Video, WebZin, WebZinArticle, WebZinArticleContent,
                     WebZinCategory, WebZinHotags)


class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name_in_manglish",)}

    class Meta:
        model = Author


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name_in_manglish",)}

    class Meta:
        model = Category


class ContentInline(admin.TabularInline):
    model = Content
    fields = ("title", "content_with_uploadImage", "advance_title", "custom_author")
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "created_date"]
    list_display_links = ["title", "created_date"]
    search_fields = ["title"]
    list_filter = ["created_date"]
    prepopulated_fields = {"slug": ("title_in_manglish",)}
    inlines = [ContentInline]

    class Meta:
        model = Article


class WebzinCatAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name_in_manglish",)}

    class Meta:
        model = WebZinCategory


@admin.register(WebZin)
class WebZinAdmin(admin.ModelAdmin):
    list_display = ["title", "title_manglish", "edition"]
    list_display_links = ["title", "edition"]
    search_fields = ["title", "title_manglish"]
    prepopulated_fields = {"slug": ("title_manglish",)}

    class Meta:
        model = WebZin


class WebZinArticleContentInline(admin.TabularInline):
    model = WebZinArticleContent
    fields = ("content", "is_subscription_needed")
    extra = 1


@admin.register(WebZinArticle)
class WebZinArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "read_time", "article_image", "published"]
    list_display_links = ["title", "article_image"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title_manglish",)}
    inlines = [WebZinArticleContentInline]

    class Meta:
        model = WebZinArticle


admin.site.register(WebZinArticleContent)
admin.site.register(SubscriptionPlan)
admin.site.register(Subscriptions)
admin.site.register(User)
admin.site.register(Review)
admin.site.register(Hotarticle)
admin.site.register(Hotags)
admin.site.register(WebZinHotags)
admin.site.register(Comment)
admin.site.register(Video)
admin.site.register(Content)

admin.site.register(WebZinCategory, WebzinCatAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
