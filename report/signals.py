import requests
from ProteinBoxBot_Core.PBB_Helpers import id_mapper
from django.db.models.signals import post_save
from django.dispatch import receiver

from report import bot_log_parser
from report.models import Property, Document


@receiver(post_save, sender=Property)
def lookup_prop_name(sender, **kwargs):
    instance = kwargs['instance']
    url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={}&props=labels&languages=en&format=json".format(
        instance.id)
    response = requests.get(url).json()
    if 'missing' in response['entities'][instance.id]:
        return
    label = response['entities'][instance.id]['labels']['en']['value']
    Property.objects.filter(pk=instance.pk).update(name=label)


@receiver(post_save, sender=Property)
def lookup_prop_formatter_url(sender, **kwargs):
    # When a prop is saved. get the formatter url
    instance = kwargs['instance']
    formatter_url = {v: k for k, v in id_mapper("P1630").items()}
    if instance.pk in formatter_url:
        Property.objects.filter(pk=instance.pk).update(formatter_url=formatter_url[instance.pk])


@receiver(post_save, sender=Document)
def process_log(sender, **kwargs):
    instance = kwargs['instance']
    task_run_pk = bot_log_parser.process_log(instance.docfile.path)