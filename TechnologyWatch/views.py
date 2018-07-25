import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from TechnologyWatch.models import Topic, Tag, Resource, Like


def root(request):
    # TODO : hottest in the last 24h ?

    context = {
        "latest": Topic.objects.order_by("-creation_date")[:20],
        "hottest": Topic.objects.annotate(likes_count=Count("like")).order_by("-likes_count")[:20],
        "tags": Tag.objects.annotate(used_count=Count("topic")).order_by("-used_count"),
        "user": request.user
    }

    return render(request, "index.html", context)


def display_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    liked_by_user = None

    if request.user.is_authenticated:
        liked_by_user = Like.objects.filter(topic=topic, liked_by=request.user).exists()

    tags = Tag.objects.annotate(used_count=Count("topic")).filter(topic=topic).order_by("-used_count")
    return render(request, "display/topic.html", {"topic": topic,
                                                  "tags": tags,
                                                  "resources": topic.resource_set.all(),
                                                  "user": request.user,
                                                  "liked_by_user": liked_by_user})


def display_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    related_topics = Topic.objects.filter(tags__name__contains=tag.name)\
                                  .annotate(likes_count=Count("like")).order_by("-likes_count")
    return render(request, "display/tag.html", {"tag": tag, "related_topics": related_topics, "user": request.user})


@login_required
def like_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    like = Like.objects.filter(topic=topic, liked_by=request.user)

    if not like.exists():
        Like.objects.create(topic=topic, liked_by=request.user)
        return HttpResponse("OK")
    else:
        return JsonResponse({"error": "Vil coquin, n'essaye pas de gruger les likes."}, status=405)


@login_required
def remove_like_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    like = Like.objects.filter(topic=topic, liked_by=request.user)

    if like.exists():
        like.delete()

    else:
        return JsonResponse({"error": "Vil coquin, n'essaye pas de gruger les likes."}, status=405)

    return HttpResponse("OK")


@login_required
def new_topic(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    form = request.POST
    print(form)

    topic = Topic.objects.filter(name=form["title"])

    if topic.exists():
        return JsonResponse({'error': "Ce sujet existe déjà."}, status=405)  # Not Allowed

    topic = Topic.objects.create(name=form["title"], description=form["description"], created_by=request.user)
    print(request.user)

    new_tags = []
    tags = []
    max_tag_length = Tag._meta.get_field('name').max_length

    for tag_name in form.getlist("tag"):

        tag_name = tag_name.strip()

        if len(tag_name) == 0:
            continue

        if tag_name in tags:
            print("Tag {} already processed, skipping...".format(tag_name))
            continue

        if len(tag_name) > max_tag_length:
            topic.delete()
            return JsonResponse({'error': "Vil coquin, essaye pas d'envoyer des requêtes malformées. Un tag ne peut "
                                          "pas faire plus de {} caractères.".format(max_tag_length)}, status=405)

        if " " in tag_name:
            topic.delete()
            return JsonResponse({'error': "Vil coquin, essaye pas d'envoyer des requêtes malformées. Un tag ne peut "
                                          "pas contenir d'espaces."}, status=405)

        tag = Tag.objects.filter(name=tag_name)

        if not tag.exists():
            tag = Tag(name=tag_name)
            new_tags.append(tag)
        else:
            tag = tag.first()

        tags.append(tag)

    for i in range(len(form.getlist("link"))):
        link = form.getlist("link")[i]

        if len(link) == 0:
            continue

        ressource = Resource(name=form.getlist("link-name")[i], link=link)
        ressource.topic = topic

        try:
            ressource.full_clean()
            ressource.save()
        except ValidationError as e:
            topic.delete()
            return JsonResponse({'error': "URL Invalide : {}".format(link)}, status=405)

    for tag in new_tags:
        tag.save()

    for tag in tags:
        topic.tags.add(tag)

    return render(request, "display/topic_created_new_tags_view.html", {"new_tags": new_tags})


def suggest_topic(request, search_value):
    if len(search_value) < 3 and search_value != "*":
        return JsonResponse({"error": "Merci de faire une recherche d'au minimum 3 caractères."}, status=400)

    topics = Topic.objects.filter(name__icontains=search_value)
    return JsonResponse([{"id": topic.id, "name": topic.name} for topic in topics], status=200, safe=False)


def suggest_tag(request, search_value):
    if len(search_value) < 3 and search_value != "*":
        return JsonResponse({"error": "Merci de faire une recherche d'au minimum 3 caractères."}, status=400)

    if search_value == "*":  # Needed to prefetch all the tags
        tags = Tag.objects.all()
    else:
        tags = Tag.objects.filter(name__icontains=search_value)

    return JsonResponse([{"id": tag.id, "name": tag.name} for tag in tags], status=200, safe=False)


def search(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    search_value = request.POST["query"]

    error = None
    topics_found = []
    tags_found = []

    if len(search_value) < 3:
        error = "Merci de faire une recherche d'au minimum 3 caractères."

    elif search_value.startswith("topic:"):
        search_value = search_value[6:]
        topics_found = Topic.objects.filter(name__iexact=search_value)

        if len(topics_found) == 1:
            return redirect(display_topic, topics_found[0].id)

        else:
            error = "Impossible de trouver ce sujet."

    elif search_value.startswith("tag:"):
        search_value = search_value[4:]
        tags_found = Tag.objects.filter(name__iexact=search_value)

        if len(tags_found) == 1:
            return redirect(display_tag, tags_found[0].id)

        else:
            error = "Impossible de trouver ce tag."

    else:
        topics_found = Topic.objects.filter(name__icontains=search_value)
        tags_found = Tag.objects.filter(name__icontains=search_value)

    if len(topics_found) == 0 and len(tags_found) == 0:
        error = "Aucun résultat trouvé pour \"{}\"".format(search_value)

    context = {
        "query": search_value,
        "topics_found": topics_found,
        "tags_found": tags_found,
        "search_error": error
    }

    return render(request, "display/search.html", context)


@login_required()
def add_resource(request, topic_id):
    if request.method != "POST":
        return HttpResponseBadRequest()

    topic = get_object_or_404(Topic, pk=topic_id)
    form = request.POST

    if len(form["link-name"]) == 0 or len(form["link"]) == 0:
        return JsonResponse({'message': "Merci de remplir tous les champs."}, status=400)

    parsed_link = requests.utils.urlparse(form["link"])

    if parsed_link.scheme != "http" and parsed_link.scheme != "https":
        return JsonResponse({'message': "L'url doit être prefixé par <b>http://</b> ou <b>https://</b>"}, status=400)

    if len(parsed_link.netloc) == 0 or len(parsed_link.netloc.split(".")) == 1:
        return JsonResponse({'message': "URL invalide."}, status=400)

    new_res = Resource()
    new_res.name = form["link-name"]
    new_res.link = form["link"]
    new_res.topic = topic
    new_res.save()

    return JsonResponse({'message': "La ressource a été ajoutée avec succès."}, status=200)


def connect(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    if request.user.is_authenticated:
        return JsonResponse({"error": "Vous êtes déjà connecté."})

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return HttpResponse("OK")

    else:
        return JsonResponse({"error": "Identifiants incorrects."}, status=401)


def disconnect(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect(root)


@login_required
def profile(request):
    context = {
        "user": request.user,

        "liked_topics": Topic.objects.filter(created_by=request.user)
                                     .order_by("-creation_date"),

        "created_topics": Topic.objects.filter(created_by=request.user)
                                       .order_by("-creation_date"),

        "comments_made": None
    }

    return render(request, "display/profile.html", context)
