from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.template.defaultfilters import slugify
from taggit.managers import TaggableManager
from taggit.models import Tag
from versatileimagefield.fields import VersatileImageField

external_plugin_resources = [
    ("youtube", "/static/ckeditor_plugins/youtube/youtube/", "plugin.js"),
    ("image2", "/static/ckeditor_plugins/image2_4.18.0/image2/", "plugin.js"),
    ("fontFamily", "/static/ckeditor_plugins/font/", "plugin.js"),
]


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create Save a User"""
        if not email:
            raise ValueError("User must have a Email")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if user:
            return user

    def create_superuser(self, email, password):
        """Create and Save a super User"""
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self.db)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ "Custom Model"""

    email = models.EmailField(max_length=225, unique=True)
    phone = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return str(self.email)


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    name_in_manglish = models.CharField(max_length=100, verbose_name="Name in Manglish")
    slug = models.SlugField(unique=True, max_length=100)

    def __str__(self):
        return self.name

    def get_articles(self):
        return Article.objects.filter(category=self)

    class Meta:
        verbose_name_plural = "Article Category"


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Author Name")
    name_in_manglish = models.CharField(max_length=100, verbose_name="Name in Manglish")
    slug = models.SlugField(unique=True, max_length=100)
    photo = VersatileImageField("Photo", blank=True, upload_to="author/")
    about = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Author"


class Article(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Category",
        related_name="articles",
    )
    author = models.ManyToManyField(Author, verbose_name="Author", blank=True)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    article_image = VersatileImageField(
        blank=True, null=True, verbose_name="Article Image", upload_to="articles/"
    )
    title = models.CharField(
        max_length=300, verbose_name="Title", blank=True, null=True
    )
    title_in_manglish = models.CharField(
        max_length=300, verbose_name="Title in Manglish"
    )
    custom_author = RichTextUploadingField(
        external_plugin_resources=[
            ("fontFamily", "/static/ckeditor_plugins/font/", "plugin.js")
        ],
        blank=True,
        null=True,
    )
    slug = models.SlugField(unique=True, max_length=100)

    read_time = models.IntegerField()
    tags = TaggableManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super(Article, self).save(*args, **kwargs)

    def get_comments(self):
        return Comment.objects.filter(article=self)

    class Meta:
        ordering = ["-created_date"]
        verbose_name_plural = "Normal Article"


class Content(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, verbose_name="Article"
    )
    title = models.CharField(
        max_length=300, verbose_name="Title", blank=True, null=True
    )
    advance_title = RichTextUploadingField(
        external_plugin_resources=external_plugin_resources,
        blank=True,
        null=True,
    )
    custom_author = RichTextUploadingField(
        external_plugin_resources=external_plugin_resources,
        blank=True,
        null=True,
    )
    content_with_uploadImage = RichTextUploadingField(
        external_plugin_resources=external_plugin_resources
    )

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = "Article Content"


class Hotags(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.name

    class Meta:
        verbose_name_plural = "Hot Tags"


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        verbose_name="Article",
        related_name="comments",
    )
    comment_author = models.CharField(max_length=100, verbose_name="Author")
    comment_content = models.CharField(max_length=200, verbose_name="Comment Content")
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_content

    class Meta:
        ordering = ["-comment_date"]
        verbose_name_plural = "Comment"


class Video(models.Model):
    youtube_link = models.CharField(max_length=300, verbose_name="Video Link")
    title = models.TextField()
    title_in_manglish = models.CharField(max_length=225)
    upload_time = models.DateTimeField(auto_now=True)
    video_thumbnail = VersatileImageField(
        verbose_name="video Thumbnail",
        upload_to="vediothumnails/",
    )
    page_contents = RichTextUploadingField(
        external_plugin_resources=[
            ("youtube", "/static/ckeditor_plugins/youtube/youtube/", "plugin.js")
        ],
        null=True,
        blank=True,
    )
    tags = TaggableManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Video"


class WebZinCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name="Category Name")
    name_in_manglish = models.CharField(max_length=50, verbose_name="Name in Manglish")
    slug = models.SlugField(unique=True, max_length=100)

    def __str__(self):
        return self.name

    def get_webzines(self):
        return WebZin.objects.filter(category=self)

    def get_articles(self):
        return WebZinArticle.objects.filter(webzinarticlecategory=self)

    class Meta:
        verbose_name_plural = "WebZine Category"


class WebZin(models.Model):
    category = models.ForeignKey(
        WebZinCategory,
        on_delete=models.CASCADE,
        verbose_name="Webzine Categoy",
        related_name="webzins",
    )
    title = models.CharField(max_length=225, verbose_name="WebZine Title")
    title_manglish = models.CharField(max_length=225, verbose_name="Title in Manglish")
    edition = models.CharField(max_length=50, verbose_name="Edition")
    publish_date = models.DateField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=100, verbose_name="URL")
    cover = VersatileImageField(
        verbose_name="WebZine Article Image",
        upload_to="webzinarticlescover/",
    )
    is_special_edition = models.BooleanField(default=False)
    single_Subscription_amount = models.IntegerField()

    def __str__(self):
        return self.title

    def get_articles(self):
        return WebZinArticle.objects.filter(webzin=self)

    class Meta:
        verbose_name_plural = "WebZine Packets"


class WebZinArticle(models.Model):
    webzin = models.ForeignKey(
        WebZin,
        on_delete=models.CASCADE,
        verbose_name="Webzine",
        related_name="webzinarticles",
    )
    webzinarticlecategory = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Category",
        related_name="webzinarticles",
    )
    title = models.CharField(max_length=300, verbose_name="Article Title")
    title_manglish = models.CharField(max_length=300, verbose_name="Title in Manglish")
    slug = models.SlugField(unique=True, max_length=100, verbose_name="URL")
    article_image = VersatileImageField(
        blank=True,
        null=True,
        verbose_name="WebZine Article Image",
        upload_to="webzinarticles/",
    )
    published = models.DateTimeField(auto_now=True)
    read_time = models.IntegerField()
    author = models.ForeignKey(
        Author, verbose_name="Author", on_delete=models.CASCADE, null=True, blank=True
    )
    tags = TaggableManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "WebZine Article"


class WebZinHotags(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.name

    class Meta:
        verbose_name_plural = "WebZin Hot Tags"


class WebZinArticleContent(models.Model):
    webzinarticle = models.ForeignKey(
        WebZinArticle,
        on_delete=models.CASCADE,
        verbose_name="Webzine Article",
        related_name="contents",
    )
    content = RichTextUploadingField(
        external_plugin_resources=external_plugin_resources
    )
    is_subscription_needed = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "WebZine Article Content"


class SubscriptionPlan(models.Model):
    subscription_title = models.CharField(max_length=225, unique=True)
    is_include_special_edition = models.BooleanField()
    validity_in_month = models.IntegerField()
    amount = models.IntegerField()

    def __str__(self):
        return self.subscription_title


class Referral(models.Model):
    agent_name = models.CharField(max_length=225)
    phone = models.CharField(max_length=225)
    referral_code = models.CharField(max_length=225)

    def __str__(self):
        return str(self.agent_name)


class Subscriptions(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    startDate = models.DateField()
    endDate = models.DateField()
    referral = models.ForeignKey(
        Referral, on_delete=models.PROTECT, blank=True, null=True
    )
    subscription_title = models.CharField(max_length=225)
    is_include_special_edition = models.BooleanField()
    razorpay_order_id = models.CharField(max_length=225, unique=True)
    status = models.CharField(max_length=100, default="Open")
    amount = models.IntegerField()

    def __str__(self):
        return self.customer.name


class SingleSubscription(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    webzin = models.ForeignKey(
        WebZin,
        on_delete=models.CASCADE,
        verbose_name="Webzine",
        related_name="singleuubscriptions",
    )
    amount = models.IntegerField()
    subscription_date = models.DateTimeField(auto_now=True)
    razorpay_order_id = models.CharField(max_length=225, unique=True)
    status = models.CharField(max_length=100, default="Open")
    referral = models.ForeignKey(
        Referral, on_delete=models.PROTECT, blank=True, null=True
    )

    def __str__(self):
        return self.customer.name + "-" + self.webzin.edition


class Review(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    review = models.TextField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.review


class Hotarticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.article)
