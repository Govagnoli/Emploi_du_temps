from django import template

register = template.Library()

#Permet de gérer les messages d'erreurs ou de succès pour l'ajout de fichier Excel
@register.filter
def messageErreursExcell(messages, tag):
    return [m for m in messages if tag in m.tags]
