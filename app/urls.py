"""TechnologyWatch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from TechnologyWatch import views

urlpatterns = [
    path('', views.root, name='root'),

    path('topic/<int:topic_id>/', views.display_topic, name="display_topic"),
    path('tag/<str:tag_id>/', views.display_tag, name="display_tag"),

    path('topic/new/', views.new_topic, name="new_topic"),
    path('topic/<int:topic_id>/like/', views.like_topic, name="upvote_topic"),
    path('topic/<int:topic_id>/removelike/', views.remove_like_topic, name="remove_upvote_topic"),
    path('topic/<int:topic_id>/addresource/', views.add_resource, name="add_resource"),

    # TODO : if there is a slash in the tag, the suggestion will not work.
    # TODO : We should use a POST request but there is a problem with the CSRF token.
    path('suggest/topic/<str:search_value>/', views.suggest_topic, name="suggest_topic"),
    path('suggest/tag/<str:search_value>/', views.suggest_tag, name="suggest_tag"),

    path('search/', views.search, name="search"),


    path('connect/', views.connect, name="connect"),
    path('disconnect/', views.disconnect, name="disconnect"),
    path('admin/', admin.site.urls, name="admin"),
] + static(settings.STATIC_URL)
