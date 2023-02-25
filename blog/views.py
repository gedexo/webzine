import datetime
import json
import re
from unicodedata import category

import razorpay
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from taggit.models import Tag
from this import s

from .forms import ReviewForm
from .models import (Article, Author, Category, Content, Hotags, Hotarticle,
                     Referral, Review, SingleSubscription, SubscriptionPlan,
                     Subscriptions, User, Video, WebZin, WebZinArticle,
                     WebZinArticleContent, WebZinCategory, WebZinHotags)


def index(request):
    latests = Article.objects.all().order_by("-id")[:3]
    hotarticles = Hotarticle.objects.filter()[:4]
    latests_articles = Article.objects.all().order_by("-id")[3:6]
    tags = Hotags.objects.all()
    webzins = WebZin.objects.all()
    categories = Category.objects.all()
    videos = Video.objects.all()
    context = {
        "is_index": True,
        "videos": videos,
        "latests": latests,
        "latests_articles": latests_articles,
        "tags": tags,
        "headercategories": categories,
        "hotarticles": hotarticles,
        "categories": categories,
        "webzins": webzins,
    }
    return render(request, "web/index.html", context)


def articles(request, slug):
    tags = Hotags.objects.all()
    category = Category.objects.get(slug=slug)
    tag_filter = False
    if request.GET.get("tag"):
        tagslug = request.GET.get("tag")
        article_list = Article.objects.filter(category=category, tags__slug=tagslug)
        tag_filter = True
    else:
        article_list = Article.objects.filter(category=category)

    paginator = Paginator(article_list, 25)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "is_article": True,
        "page_obj": page_obj,
        "category": category,
        "tag_filter": tag_filter,
        "tags": tags,
    }
    return render(request, "web/articlesPage.html", context)


def videos(request):
    tags = Hotags.objects.all()
    videos_list = Video.objects.all()
    paginator = Paginator(videos_list, 25)
    page_number = request.GET.get("page")
    videos = paginator.get_page(page_number)
    context = {"is_videos": True, "videos": videos, "tags": tags}
    return render(request, "web/videosPage.html", context)


def video(request, id):
    tags = Hotags.objects.all()
    video = Video.objects.get(id=id)
    v_tags = video.tags.all()
    context = {"video": video, "v_tags": v_tags, "tags": tags}
    return render(request, "web/videosingle.html", context)


def taggedarticles(request, slug):
    tags = Hotags.objects.all()
    tag = get_object_or_404(Hotags, tag__slug=slug)
    categories = Category.objects.all()
    videos = Video.objects.filter(tags__slug=slug)
    context = {
        "is_index": True,
        "categories": categories,
        "videos": videos,
        "tags": tags,
        "tag": tag,
    }
    return render(request, "web/taggedarticles.html", context)


def webzintaggedarticles(request, slug):
    tags = WebZinHotags.objects.all()
    categories = Category.objects.all()
    tag = Tag.objects.get(slug=slug)
    videos = Video.objects.filter(tags__slug=slug)
    context = {
        "is_index": True,
        "categories": categories,
        "videos": videos,
        "videosection": videos.exists(),
        "tag": tag,
        "tags": tags,
    }
    return render(request, "web/webzintagged.html", context)


def article(request, slug):
    comments = Review.objects.filter(article__slug=slug).order_by("-id")[:10]
    article = Article.objects.get(slug=slug)
    tags = article.tags.all()
    contents = Content.objects.filter(article=article)
    relatedarticles = Article.objects.filter(category=article.category)[:3]

    form = ReviewForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.article = article
            data.save()
            response_data = {
                "status": "true",
                "title": "Successfully Submitted",
                "message": "Comment successfully submitted",
            }
        else:
            print(form.errors)
            response_data = {
                "status": "false",
                "title": "Form validation error",
                "message": repr(form.errors),
            }
        return HttpResponse(
            json.dumps(response_data), content_type="application/javascript"
        )
    else:
        context = {
            "is_article": True,
            "article": article,
            "contents": contents,
            "tags": tags,
            "relatedarticles": relatedarticles,
            "form": form,
            "comments": comments,
        }
        return render(request, "web/articlesingle.html", context)


def article_of_author(request, id):
    categories = Category.objects.all()
    tags = Hotags.objects.all()
    author = Author.objects.get(id=id)

    class AuthorPageItems:
        def __init__(self, category, articles):
            self.category = category
            self.articles = articles

    PageItems = []
    for category in categories:
        if Article.objects.filter(author__id__in=[id], category=category).exists():
            PageItems.append(
                AuthorPageItems(
                    category,
                    Article.objects.filter(author__id__in=[id], category=category),
                )
            )

    context = {
        "is_author": True,
        "author": author,
        "PageItems": PageItems,
        "tags": tags,
        "is_webzine": True,
    }
    context["is_webzine"] = True
    return render(request, "web/AuthorsArticle.html", context)


def webzin_article_of_author(request, id):
    tags = WebZinHotags.objects.all()
    author = Author.objects.get(id=id)
    webzinearticle = WebZinArticle.objects.filter(author=author)
    context = {
        "is_author": True,
        "author": author,
        "tags": tags,
        "webzinearticle": webzinearticle,
        "is_webzine": True,
    }
    return render(request, "web/WebZineAuthorsArticle.html", context)


def webzinViewAll(request):
    webzins = WebZin.objects.all()
    context = {"webzin_index": True, "webzins": webzins, "is_webzine": True}
    return render(request, "web/webzinviewall.html", context)


def about(request):
    return render(request, "web/about.html")


def terms(request):
    return render(request, "web/terms.html")


def webzinLatest(request):
    hotags = WebZinHotags.objects.all()
    webzins = WebZin.objects.all()
    webzin = WebZin.objects.first()
    webzinArticleCategory = Category.objects.all()
    context = {
        "webzinlatest_index": True,
        "webzins": webzins,
        "webzin": webzin,
        "webzinArticleCategory": webzinArticleCategory,
        "hotags": hotags,
        "is_webzine": True,
    }
    return render(request, "web/webzinlatest.html", context)


def SingleWebzin(request, slug):
    hotags = WebZinHotags.objects.all()
    webzin = WebZin.objects.get(slug=slug)
    articles_under_webzin = WebZinArticle.objects.filter(webzin=webzin)
    websincategory = WebZin.objects.filter(slug=slug)
    webzinarticlecategories = []
    for article in articles_under_webzin:
        if article.webzinarticlecategory not in webzinarticlecategories:
            webzinarticlecategories.append(article.webzinarticlecategory)

    class IndexPageItems:
        def __init__(self, category, articles):
            self.category = category
            self.articles = articles

    pageItems = []
    for webzinarticlecategy in webzinarticlecategories:
        if (
            WebZinArticle.objects.filter(
                webzinarticlecategory=webzinarticlecategy
            ).count()
            > 0
        ):
            pageItems.append(
                IndexPageItems(
                    webzinarticlecategy,
                    list(
                        WebZinArticle.objects.filter(
                            webzinarticlecategory=webzinarticlecategy
                        )
                    ),
                )
            )
    webzinarticles = WebZinArticle.objects.filter(webzin=webzin)

    class WhatsappIntance:
        def __init__(self, title, summary):
            self.title = title
            self.summary = summary

    instance = WhatsappIntance(webzin.title, webzin.edition)

    context = {
        "webzin": webzin,
        "webzinarticles": webzinarticles,
        "webzinarticlecategories": webzinarticlecategories,
        "pageItems": pageItems,
        "webzin": webzin,
        "hotags": hotags,
        "instance": instance,
    }
    return render(request, "web/webzinsingle.html", context)


def SingleWebzinArticle(request, slug):
    webzinhotTags = WebZinHotags.objects.all()
    webzinArticle = WebZinArticle.objects.get(slug=slug)
    relatedarticles = WebZinArticle.objects.filter(
        webzinarticlecategory=webzinArticle.webzinarticlecategory
    ).exclude(id=webzinArticle.id)[:3]
    atricleTags = webzinArticle.tags.all()
    is_subscribed = False
    contents = WebZinArticleContent.objects.filter(
        webzinarticle=webzinArticle, is_subscription_needed=False
    )
    if request.user.is_authenticated:
        user = request.user
        specialEdition = webzinArticle.webzin.is_special_edition
        current_date = datetime.datetime.now().date()
        publish_date = webzinArticle.webzin.publish_date
        # Checking if the user has any subscriptions
        if specialEdition:
            if (
                Subscriptions.objects.filter(
                    customer=user,
                    startDate__lte=current_date,
                    endDate__gte=current_date,
                    is_include_special_edition=True,
                    status="Paid",
                )
                or request.user.is_superuser
            ):
                contents = WebZinArticleContent.objects.filter(
                    webzinarticle=webzinArticle
                )
                is_subscribed = True
        else:
            if (
                Subscriptions.objects.filter(
                    customer=user,
                    startDate__lte=current_date,
                    endDate__gte=current_date,
                    status="Paid",
                )
                or request.user.is_superuser
            ):
                contents = WebZinArticleContent.objects.filter(
                    webzinarticle=webzinArticle
                )
                is_subscribed = True

        # Checking if the user has a single-subscription.
        if SingleSubscription.objects.filter(
            customer=request.user,
            webzin=webzinArticle.webzin,
            status="Paid",
        ):
            contents = WebZinArticleContent.objects.filter(webzinarticle=webzinArticle)
            is_subscribed = True
        else:
            print(
                "This user : ",
                request.user,
                " doesnt have single subscription for this",
            )
    context = {
        "webzinArticle": webzinArticle,
        "contents": contents,
        "is_subscribed": is_subscribed,
        "atricleTags": atricleTags,
        "webzinhotTags": webzinhotTags,
        "slug": webzinArticle.webzin.slug,
        "relatedarticles": relatedarticles,
        "is_webzine": True,
    }
    return render(request, "web/webzinsinglearticle.html", context)


def webzinarticles(request, slug):
    tags = Hotags.objects.all()
    category = Category.objects.get(slug=slug)
    tag_filter = False
    if request.GET.get("tag"):
        tagslug = request.GET.get("tag")
        article_list = WebZinArticle.objects.filter(
            webzinarticlecategory=category, tags__slug=tagslug
        )
        tag_filter = True
    else:
        article_list = WebZinArticle.objects.filter(webzinarticlecategory=category)

    paginator = Paginator(article_list, 25)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "category": category,
        "tag_filter": tag_filter,
        "tags": tags,
        "is_webzine": True,
    }
    return render(request, "web/webZinarticlesPage.html", context)


def login(request):
    error = ""
    if request.POST:
        username = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if request.GET.get("next"):
                return redirect(request.GET.get("next"))
            return redirect("/")
        else:
            error = "Incorrect Username or password"
    context = {"error": error}
    return render(request, "web/login.html", context)


def register(request):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    error = ""
    context = {}
    if request.POST:
        name = request.POST["name"]
        phone = request.POST["phone"]
        email = request.POST["email"]
        password = request.POST["password"]
        password1 = request.POST["password1"]
        context["name"] = name
        context["phone"] = phone
        context["email"] = email
        context["password"] = password
        context["password1"] = password1
        if not re.fullmatch(regex, email):
            error = "Enter Valid Email"
            context["error"] = error
            return render(request, "web/register.html", context)
        if password != password1:
            context["error1"] = "Password mismatch"
            return render(request, "web/register.html", context)
        if User.objects.filter(email=email).exists():
            context["error"] = "Email Already Registered Please Login"
            return render(request, "web/register.html", context)

        get_user_model().objects.create_user(
            email=email, password=password, name=name, phone=phone
        )
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            if request.GET.get("next"):
                return redirect(request.GET.get("next"))
            return redirect("/")
    return render(request, "web/register.html", context)


@login_required(login_url="blog:login")
def subscription(request, slug):
    webzin = WebZin.objects.get(slug=slug)
    subscriptionplan = SubscriptionPlan.objects.all()
    context = {"subscriptionplan": subscriptionplan, "webzin": webzin}
    return render(request, "web/subscription.html", context)


@login_required(login_url="blog:login")
def subscriptions(request):
    subscriptionplan = SubscriptionPlan.objects.all()
    context = {
        "subscriptionplan": subscriptionplan,
    }
    return render(request, "web/subscriptions.html", context)


razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
)


@login_required(login_url="blog:login")
def subscribe(request, id):
    subscriptionplan = SubscriptionPlan.objects.get(id=id)
    currency = "INR"
    amount = subscriptionplan.amount * 100

    if Subscriptions.objects.filter(customer=request.user).exists():
        referral = Subscriptions.objects.filter(customer=request.user).last().referral
        if referral:
            referral_code = referral.referral_code
            context["referral_code"] = referral_code

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(
        dict(amount=amount, currency=currency, payment_capture="0")
    )

    # order id of newly created order.
    razorpay_order_id = razorpay_order["id"]
    callback_url = "/subscriptionhandler/"

    Subscriptions.objects.create(
        customer=request.user,
        razorpay_order_id=razorpay_order_id,
        startDate=datetime.datetime.now(),
        endDate=datetime.datetime.now()
        + relativedelta(months=subscriptionplan.validity_in_month),
        subscription_title=subscriptionplan.subscription_title,
        is_include_special_edition=subscriptionplan.is_include_special_edition,
        amount=subscriptionplan.amount,
    )
    context = {
        "subscriptionplan": subscriptionplan,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_merchant_key": settings.RAZOR_KEY_ID,
        "razorpay_amount": amount,
        "currency": currency,
        "callback_url": callback_url,
    }
    return render(request, "web/subscribe.html", context)


@login_required(login_url="blog:login")
def single_subscribe(request, id):
    webzin = WebZin.objects.get(id=id)
    currency = "INR"
    referral_code = None
    amount = webzin.single_Subscription_amount * 100
    if SingleSubscription.objects.filter(customer=request.user).exists():
        referral = (
            SingleSubscription.objects.filter(customer=request.user).last().referral
        )
        if referral:
            referral_code = referral.referral_code

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(
        dict(amount=amount, currency=currency, payment_capture="0")
    )

    # order id of newly created order.
    razorpay_order_id = razorpay_order["id"]
    callback_url = "/singlesubscriptionhandler/"

    SingleSubscription.objects.create(
        customer=request.user,
        razorpay_order_id=razorpay_order_id,
        subscription_date=datetime.datetime.now(),
        webzin=webzin,
        amount=webzin.single_Subscription_amount,
    )

    context = {
        "webzin": webzin,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_merchant_key": settings.RAZOR_KEY_ID,
        "razorpay_amount": amount,
        "currency": currency,
        "callback_url": callback_url,
    }
    return render(request, "web/singlesubscribe.html", context)


@csrf_exempt
def SubscriptionHandler(request):
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get("razorpay_payment_id", "")
            razorpay_order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            rupees = (
                Subscriptions.objects.get(razorpay_order_id=razorpay_order_id).amount
                * 100
            )

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result:
                amount = rupees
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    subscription = Subscriptions.objects.get(
                        razorpay_order_id=razorpay_order_id
                    )
                    subscription.status = "Paid"
                    subscription.save()
                    # render success page on successful caputre of payment
                    return render(request, "web/paymentsuccess.html")
                except:
                    # if there is an error while capturing payment.
                    return render(request, "web/paymentfail.html")
            else:
                # if signature verification fails.
                return render(request, "web/paymentfail.html")
        except Exception:
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()


@csrf_exempt
def SingleSubscriptionHandler(request):
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get("razorpay_payment_id", "")
            razorpay_order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            rupees = (
                SingleSubscription.objects.get(
                    razorpay_order_id=razorpay_order_id
                ).amount
                * 100
            )

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result:
                amount = rupees
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    subscription = SingleSubscription.objects.get(
                        razorpay_order_id=razorpay_order_id
                    )
                    subscription.status = "Paid"
                    subscription.save()
                    # render success page on successful caputre of payment
                    return render(request, "web/paymentsuccess.html")
                except:
                    # if there is an error while capturing payment.
                    return render(request, "web/paymentfail.html")
            else:
                # if signature verification fails.
                return render(request, "web/paymentfail.html")
        except Exception:
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()


@csrf_exempt
def add_referrel_code(request):
    if request.method == "POST":
        code = request.POST["code"]
        orderId = request.POST["orderId"]
        subscription = Subscriptions.objects.get(razorpay_order_id=orderId)
        if Referral.objects.filter(referral_code=code).exists():
            referObject = Referral.objects.get(referral_code=code)
            subscription.referral = referObject
            subscription.save()
        else:
            return HttpResponseBadRequest()

    return JsonResponse({"meassage": "success"})


@csrf_exempt
def add_referrel_code_single(request):
    if request.method == "POST":
        code = request.POST["code"]
        orderId = request.POST["orderId"]
        subscription = SingleSubscription.objects.get(razorpay_order_id=orderId)
        if Referral.objects.filter(referral_code=code).exists():
            referObject = Referral.objects.get(referral_code=code)
            subscription.referral = referObject
            subscription.save()
        else:
            return HttpResponseBadRequest()
    return JsonResponse({"meassage": "success"})


def privacypolicy(request):
    return render(request, "web/privacypolicy.html")


def cancellationypolicy(request):
    return render(request, "web/cancellationypolicy.html")


def logout_view(request):
    logout(request)
    return redirect("/")
