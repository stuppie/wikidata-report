import copy
from collections import Counter

from django.db.models import Max
from rest_framework import serializers

from .models import *


"""
Handle wdapierror:
{'error': {'*': 'See https://www.wikidata.org/w/api.php for API usage',
  'code': 'failed-save',
  'info': 'The link [https://fr.wikipedia.org/wiki/Histiocytose_langerhansienne frwiki:Histiocytose langerhansienne] is already used by item [[Q374036|Q374036]]. You may remove it from [[Q374036|Q374036]] if it does not belong there or merge the items if they are about the exact same topic.',
  'messages': [{'html': {'*': 'The link <a class="external text" href="https://fr.wikipedia.org/wiki/Histiocytose_langerhansienne">frwiki:Histiocytose langerhansienne</a> is already used by item <a href="/wiki/Q374036" title="Q374036">Q374036</a>. You may remove it from <a href="/wiki/Q374036" title="Q374036">Q374036</a> if it does not belong there or merge the items if they are about the exact same topic.'},
    'name': 'wikibase-validator-sitelink-conflict',
    'parameters': ['[https://fr.wikipedia.org/wiki/Histiocytose_langerhansienne frwiki:Histiocytose langerhansienne]',
     '[[Q374036|Q374036]]']}]},
 'servedby': 'mw1225'}
 """

class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        response = {
            'id': obj.pk,
            'name': obj.name,
        }
        # Item.objects.annotate(last_touched=Max('log__timestamp')).last_touched
        response['last_touched'] = obj.log_set.order_by("-timestamp").first().timestamp
        response['tasks'] = obj.log_set.values_list("task_run_id", flat=True)
        response['task_names'] = list(set(obj.log_set.values_list("task_run__task_id", flat=True)))
        return response

    class Meta:
        model = Item


class TaskSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        return {
            'name': obj.name,
            'maintainer': obj.maintainer.name,
            'email': obj.maintainer.email,
            'tags': obj.tags.all().values_list("name", flat=True)
        }

    class Meta:
        model = Task


class SourceSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        return {
            'name': obj.name,
            'url': obj.url,
            'release': obj.release,
            'timestamp': obj.timestamp,
            'wdid': obj.item.id
        }

    class Meta:
        model = Source


class BriefTaskRunSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        response = {
            'id': obj.pk,
            'name': obj.name,
            'task_name': obj.task.name,
            'timestamp': obj.timestamp,
            'maintainer': obj.task.maintainer.name
        }
        return response

class TaskRunSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        response = {
            'id': obj.pk,
            'name': obj.name,
            'task_name': obj.task.name,
            'timestamp': obj.timestamp,
            'maintainer': obj.task.maintainer.name
        }
        # get started and ended time from logs associated with this run
        logs = Log.objects.filter(task_run__pk=obj.pk).order_by("timestamp")
        started = logs.first().timestamp
        ended = logs.last().timestamp
        response.update({
            'started': started,
            'ended': ended
        })

        # get counts of all levels from logs
        levels = dict(Counter(logs.values_list("level", flat=True)))
        total = sum(levels.values())
        response['messages'] = {"counts": copy.copy(levels)}
        response['messages']["counts"]['__total__'] = total

        for level in levels:
            # get counts of all messages from logs that are type 'level'
            messages = dict(Counter(logs.filter(level=level).values_list("msg", flat=True)))
            response['messages'].update({level: messages})

        # get sources used for this run
        response['sources'] = SourceSerializer(obj.sources.all(), many=True).data

        return response

    class Meta:
        model = TaskRun


class LogSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        return {
            # 'bot_run': BotRunSerializer().to_representation(obj.bot_run),
            'run_id': obj.task_run.id,
            'run_name': obj.task_run.name,
            'task_name': obj.task_run.task.name,
            'wdid': obj.wdid.id,
            'timestamp': obj.timestamp,
            'level': obj.level,
            'external_id': obj.external_id,
            'external_id_prop': obj.external_id_prop.id,
            'msg': obj.msg
        }

    class Meta:
        model = Log
