from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from TechnologyWatch.models import Topic, Tag, Resource, Like
import requests


def root(request):

    # TODO : hottest in the last 24h ?

    context = {
        "latest": Topic.objects.annotate(likes_count=Count("like")).order_by("-creation_date")[:20],
        "hottest": Topic.objects.annotate(likes_count=Count("like")).order_by("-likes_count")[:20],
        "tags": Tag.objects.annotate(used_count=Count("topic")).order_by("-used_count")
    }

    return render(request, "index.html", context)


def display_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    tags = Tag.objects.annotate(used_count=Count("topic")).filter(topic=topic).order_by("-used_count")
    return render(request, "display/topic.html", {"topic": topic,
                                                  "likes_count": topic.like_set.count(),
                                                  "tags": tags,
                                                  "resources": topic.resource_set.all()})


def display_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    related_topics = Topic.objects.filter(tags__name__contains=tag.name)
    related_topics = related_topics.annotate(likes_count=Count("like"))
    related_topics = related_topics.order_by("-likes_count")
    return render(request, "display/tag.html", {"tag": tag, "related_topics": related_topics})


def like_topic(request, topic_id):
    # TODO : check that the user doesn't have voted already

    topic = get_object_or_404(Topic, pk=topic_id)
    user = None
    like = Like.objects.filter(topic=topic, user=user).first()

    if like is None:
        like = Like()
        like.topic = topic
        like.save()
    else:
        return JsonResponse({"error": "Vil coquin, n'essaye pas de gruger les likes."}, status=405)

    return HttpResponse("OK")


def remove_like_topic(request, topic_id):
    # TODO : check that the user has voted already

    topic = get_object_or_404(Topic, pk=topic_id)
    user = None
    like = Like.objects.filter(topic=topic, user=user).first()

    if like is not None:
        like.delete()

    else:
        return JsonResponse({"error": "Vil coquin, n'essaye pas de gruger les likes."}, status=405)

    return HttpResponse("OK")


def new_topic(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    form = request.POST
    print(form)
    return HttpResponse("OK")

    existing_topic = Topic.objects.filter(name=form["title"])

    if len(existing_topic) == 1:
        return JsonResponse({'error': "Ce sujet existe déjà."}, status=405)  # Not Allowed

    topic = Topic(name=form["title"],
                  description=form["description"],
                  # tags=[],
                  # ressources=[]
                  )

    topic.save()

    new_tags = []

    return render(request, "display/topic_created_new_tags_view.html", new_tags)


def suggest_topic(request, search_value):
    if len(search_value) < 3:
        return JsonResponse({"error": "Merci de faire une recherche d'au minimum 3 caractères."}, status=400)

    topics = Topic.objects.filter(name__icontains=search_value)
    return JsonResponse([{"id": topic.id, "name": topic.name} for topic in topics], status=200, safe=False)


def suggest_tag(request, search_value):
    if len(search_value) < 3:
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
    error_code = None
    topics_found = []
    tags_found = []

    if len(search_value) < 3:
        error = "Merci de faire une recherche d'au minimum 3 caractères."
        error_code = 400

    elif search_value.startswith("topic:"):
        search_value = search_value[6:]
        topics_found = Topic.objects.filter(name__iexact=search_value)

        if len(topics_found) == 1:
            return redirect(display_topic, topics_found[0].id)

        else:
            error = "Impossible de trouver ce sujet."
            error_code = 404

    elif search_value.startswith("tag:"):
        search_value = search_value[4:]
        tags_found = Tag.objects.filter(name__iexact=search_value)

        if len(tags_found) == 1:
            return redirect(display_tag, tags_found[0].id)

        else:
            error = "Impossible de trouver ce tag."
            error_code = 404

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
    return None


def disconnect(request):
    return None