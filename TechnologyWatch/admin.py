from django.contrib import admin
from TechnologyWatch.models import Tag, Topic, Ressource, Like


#@admin.register(Category)
#class CategoryAdmin(admin.ModelAdmin):
#    pass


admin.site.register(Tag)
admin.site.register(Topic)
admin.site.register(Ressource)
admin.site.register(Like)
