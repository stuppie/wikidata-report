from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_filters import Filter
from django_filters.fields import Lookup
from rest_framework import viewsets

from report.forms import DocumentForm
from report.models import TaskRun, Task, Log, Item, Document
from report.serializers import TaskSerializer, TaskRunSerializer, LogSerializer, ItemSerializer, BriefTaskRunSerializer
from . import bot_log_parser


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskRunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskRun.objects.all()
    serializer_class = TaskRunSerializer

    def get_queryset(self):
        queryset = TaskRun.objects.all()
        run_name = self.request.query_params.get('run_name', None)
        if run_name is not None:
            queryset = queryset.filter(name=run_name)
        id = self.request.query_params.get('id', None)
        if id is not None:
            queryset = queryset.filter(id=id)
        task_name = self.request.query_params.get('task_name', None)
        if task_name is not None:
            queryset = queryset.filter(task__name=task_name)
        brief = self.request.query_params.get('brief', None)
        if brief == "1":
            self.serializer_class = BriefTaskRunSerializer

        return queryset

    def filter_queryset(self, queryset):
        queryset = super(TaskRunViewSet, self).filter_queryset(queryset)
        queryset = queryset.order_by("timestamp")
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset


class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer

    def get_queryset(self):
        queryset = self.queryset
        wdid = self.request.query_params.get('wdid', None)
        level = self.request.query_params.get('level', None)
        task_name = self.request.query_params.get('task_name', None)
        run_name = self.request.query_params.get('run_name', None)
        run = self.request.query_params.get('run', None)
        msg = self.request.query_params.get('msg', None)
        if wdid is not None:
            queryset = queryset.filter(wdid=wdid)
        if level is not None:
            queryset = queryset.filter(level=level)
        if task_name is not None:
            queryset = queryset.filter(task_run__task__name=task_name)
        if run_name is not None:
            queryset = queryset.filter(task_run__name=run_name)
        if run is not None:
            queryset = queryset.filter(task_run=run)
        if msg is not None:
            queryset = queryset.filter(msg=msg)

        return queryset


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = self.queryset
        wdid = self.request.query_params.get('id', None)
        if wdid is not None:
            queryset = ListFilter(name="id").filter(queryset, wdid)
        return queryset


class ListFilter(Filter):
    def filter(self, qs, value):
        value_list = value.split(u',')
        return super(ListFilter, self).filter(qs, Lookup(value_list, 'in'))


def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()
            return HttpResponseRedirect('/taskrun/')
    else:
        form = DocumentForm()  # A empty, unbound form

    # Render list page with the documents and the form
    return render(request, 'upload.html', {'form': form})

from io import StringIO
from django.http import HttpResponse

@csrf_exempt
def uploadPOST(request):
    """
    import requests
    url = "http://127.0.0.1:8080/uploadPOST/"
    f = "/home/gstupp/projects/biothings/wikidata/media/test.log"
    data = open(f).read()
    r=requests.post(url, data=data)
    """
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        with open("media/tmp.tmp",'w') as f:
            f.write(data)
        newdoc = Document(docfile="tmp.tmp")
        newdoc.save()
        print("done saving")
        return HttpResponse("done")

    return HttpResponse('it was GET request')