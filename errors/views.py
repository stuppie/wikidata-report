"""
d = {"servedby": "mw1276",
     "error": {"code": "modification-failed",
               "info": "Item [[Q27826279|Q27826279]] already has label \"The importance of an innervated and intact antrum and pylorus in preventing postoperative duodenogastric reflux and gastritis.\" associated with language code en, using the same description text.",
               "*": "See https://www.wikidata.org/w/api.php for API usage",
               "messages": [{"name": "wikibase-validator-label-with-description-conflict",
                             "html": {
                                 "*": "Item <a href=\"/wiki/Q27826279\" title=\"Q27826279\">Q27826279</a> already has label \"The importance of an innervated and intact antrum and pylorus in preventing postoperative duodenogastric reflux and gastritis.\" associated with language code en, using the same description text."},
                             "parameters": [
                                 "The importance of an innervated and intact antrum and pylorus in preventing postoperative duodenogastric reflux and gastritis.",
                                 "en",
                                 "[[Q27826279|Q27826279]]"]}
                            ]
               }
     }

d['error']['code']  # 'modification-failed'
d['error']['info']  # description

d['error']['messages'][0]['name']  # 'wikibase-validator-label-with-description-conflict'
d['error']['messages'][0]['html']['*']
"""
import json

from django.shortcuts import render

from report.models import Log


def format_wdapierror(d):
    return {'code': d['error']['code'],
            'info': d['error']['info'],
            'name': d['error']['messages'][0]['name'],
            'html': d['error']['messages'][0]['html']['*'].replace("<a href=\"/wiki",
                                                                   "<a href=\"https://www.wikidata.org/wiki")}


def index(request):
    logs = Log.objects.filter(level="ERROR", task_run=18)[:5]
    for log in logs:
        if log.msg_type and "ProteinBoxBot_Core.PBB_Core" in log.msg_type:
            log.error_type = "PBB_Core"
            log.msg = format_wdapierror(json.loads(log.msg))
            print(log.msg)
        else:
            log.error_type = "default"
        if log.external_id_prop.formatter_url:
            log.url = log.external_id_prop.formatter_url.replace("$1", log.external_id)
        else:
            log.url = None
    context = {
        'errors': logs,
    }
    return render(request, 'errors.html', context)
