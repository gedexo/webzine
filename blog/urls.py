from django.urls import path

from . import views

app_name = "blog"


urlpatterns = [
    path("", views.index, name="home"),
    path("accounts/login/", views.login, name="login"),
    path("register", views.register, name="register"),
    path("subscription/<slug:slug>/", views.subscription, name="subscription"),
    path("about/", views.about, name="about"),
    path("privacypolicy/", views.privacypolicy, name="privacypolicy"),
    path("cancellationypolicy/", views.cancellationypolicy, name="cancellationypolicy"),
    path("logout/", views.logout_view, name="logout"),
    path("terms/", views.terms, name="terms"),
    path("subscriptions/", views.subscriptions, name="subscriptions"),
    path("subscribe/<int:id>", views.subscribe, name="subscribe"),
    path("singlesubscribe/<int:id>", views.single_subscribe, name="singlesubscribe"),
    path("article/<slug:slug>", views.article, name="article"),
    path("articles/<slug:slug>/", views.articles, name="articles"),
    path("tags/<slug:slug>/", views.taggedarticles, name="taggedarticles"),
    path("webzin-tags/<slug:slug>", views.webzintaggedarticles, name="webzin-tags"),
    path("videos/", views.videos, name="videos"),
    path("video/<int:id>", views.video, name="video"),
    path("author/<int:id>", views.article_of_author, name="author"),
    path("webzin-author/<int:id>", views.webzin_article_of_author, name="webzinauthor"),
    path("latest-webzin", views.webzinLatest, name="latest"),
    path("webzins", views.webzinViewAll, name="webzins"),
    path("webzin/<slug:slug>", views.SingleWebzin, name="webzin"),
    path("webzinarticles/<slug:slug>/", views.webzinarticles, name="webzinarticles"),
    path("webzinarticle/<slug:slug>", views.SingleWebzinArticle, name="webzinarticle"),
    path("subscriptionhandler/", views.SubscriptionHandler, name="subscriptionhandler"),
    path(
        "singlesubscriptionhandler/",
        views.SingleSubscriptionHandler,
        name="singlesubscriptionhandler",
    ),
    path("add-referrel-code/", views.add_referrel_code, name="add-referrel-code"),
    path(
        "add-referrel-code-single/",
        views.add_referrel_code_single,
        name="add-referrel-code-single",
    ),
]
