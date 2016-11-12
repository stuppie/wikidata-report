import glob
import json
import os
import sys

import pandas as pd
from dateutil.parser import parse as dateutil_parse

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "wikidata.settings"

import django

django.setup()
from report.models import Person, TaskRun, Task, Tag, Item, Log, Property, Source


def get_or_create_task(task_name, maintainer=None, tags=None, properties=None):
    """

    :param task_name:
    :type task_name: str
    :param maintainer:
    :type maintainer: str
    :param tags:
    :type tags: List[str]
    :param properties:
    :type properties: List[str]
    :return:
    """
    tags = tags if tags else []
    properties = properties if properties else []

    if not Task.objects.filter(name=task_name).exists():
        assert maintainer is not None
        person, _ = Person.objects.get_or_create(name=maintainer)
        task = Task.objects.create(name=task_name, maintainer=person)
    else:
        task = Task.objects.get(name=task_name)
    for tag in tags:
        task.tags.add(Tag.objects.get_or_create(name=tag)[0])
    for property in properties:
        task.properties.add(Property.objects.get_or_create(id=property)[0])
    return task


def create_task_run(task, run_name, timestamp, sources=None):
    """

    :param task:
    :param run_name:
    :param timestamp:
    :param sources:  {'ensembl': {'_id': 'ensembl', 'release': 86, 'timestamp': '20161005'},
                     'entrez': {'_id': 'entrez', 'timestamp': '20161029'},
                     'uniprot': {'_id': 'uniprot', 'timestamp': '20161103'}}
    :return:
    """
    tr_qs = TaskRun.objects.filter(task=task, name=run_name, timestamp=timestamp)
    if tr_qs.exists():
        tr = next(tr_qs.iterator())
        print("Error! Task {} already exists.".format(tr))
        return None
    else:
        task_run = TaskRun.objects.create(task=task, name=run_name, timestamp=timestamp)
    sources = sources if sources else dict()
    for source, source_info in sources.items():
        source_model, _ = Source.objects.get_or_create(name=source, release=source_info.get("release", None),
                                                       timestamp=source_info.get("timestamp", None))
        task_run.sources.add(source_model)
    return task_run


def django_log_pd(task_run, row):
    item = Item.objects.get_or_create(id=row.wdid)[0]
    prop, created = Property.objects.get_or_create(id=row.prop)
    if created:
        print("Property created: {}".format(prop))
    return Log(wdid=item, timestamp=row.timestamp, task_run=task_run, level=row.level, external_id=row.external_id,
               external_id_prop=prop, msg=row.msg)


def parse_log(file_path):
    df = pd.read_csv(file_path, sep=",", names=['level', 'timestamp', 'external_id', 'prop', 'wdid', 'msg', 'msg_type'],
                     dtype={'external_id': str}, comment='#', quotechar='"', skipinitialspace=True, delimiter=';')
    df.fillna('', inplace=True)
    df = df.apply(lambda x: x.str.strip())
    df.timestamp = pd.to_datetime(df.timestamp, format='%m/%d/%Y %H:%M:%S')
    return df


def process_log(file_path):
    """
    Expects header as first line in log file. Header begins with comment character '#'. The line is a json string dump of
    a dictionary that contains the following keys:
    name: str, Task name
    maintainer: str, Name of person
    tags: list of tags associated with the task. can be empty
    properties: list of properties associated with the task. can be empty
    run_id: str, a run ID for the task run
    timestamp: str, timestamp for the task run

    :param file_path:
    :return:
    """
    # TODO: http://stackoverflow.com/questions/27858539/python-logging-module-emits-wrong-timezone-information/27858760#27858760

    # read header
    if isinstance(file_path, str):
        with open(file_path) as f:
            line = f.readline()
    else:
        line = file_path.readline()
    if not line.startswith("#"):
        raise ValueError("Expecting header in log file")
    metadata = json.loads(line[1:])
    print(metadata)

    task = get_or_create_task(metadata['name'], maintainer=metadata['maintainer'], tags=metadata['tags'],
                              properties=metadata['properties'])
    task_run = create_task_run(task, metadata['run_id'], dateutil_parse(metadata['timestamp']),
                               sources=metadata.get('sources', None))
    if not task_run:
        return

    df = parse_log(file_path)
    log_items = list(df.apply(lambda row: django_log_pd(task_run, row), axis=1))
    Log.objects.bulk_create(log_items)

    return task_run.pk


def process_logs(log_dir):
    for file_path in glob.glob(os.path.join(log_dir, "*.log")):
        process_log(file_path)


if __name__ == "__main__":
    process_log(sys.argv[1])
