from django.contrib import admin
from CollaborativeTechnologyWatch.models import Tag, Topic, Resource, Like


#@admin.register(Category)
#class CategoryAdmin(admin.ModelAdmin):
#    pass


admin.site.register(Tag)
admin.site.register(Topic)
admin.site.register(Resource)
admin.site.register(Like)
