import json
import math

from django.db.models import Q
from django.core import serializers
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed

from project.main.models import *


def index(request):
    prjs = Project.objects.all()
    context = {
        'title': '',
        'prjs': prjs,
        'current_menu': 'Home'
    }
    return render(request, 'main/index.html', context)


def project(request, id=False):
    prj = False
    exps = False
    conds = False
    if id:
        prj = Project.objects.get(id=id)
        exps = Experiment.objects.filter(Q(condition1__prj__id=id) | Q(condition2__prj__id=id))
    context = {
        'title': 'Project',
        'prj': prj,
        'exps': exps,
        'current_menu': 'Projects'
    }
    return render(request, 'main/project.html', context)


def experiment(request, id=False):
    exp = Experiment.objects.get(id=id)
    exps = Experiment.objects.filter(
        Q(condition1__prj__id=exp.condition1.prj_id) | Q(condition2__prj__id=exp.condition1.prj_id))
    context = {
        'title': 'Experiment',
        'exp': exp,
        'exps': exps,
        'current_menu': 'Experiment'
    }
    return render(request, 'main/experiment.html', context)


def service(request):
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    response = dict()
    try:
        data = json.loads(request.POST['query'])
    except KeyError:
        return HttpResponseNotAllowed(['POST'])

    if data['operation'] == "search":
        if data['property'] == 'expintron':
            response['success'] = False
            if data['value']:
                value = json.loads(data['value'])
                if 'exp_id' in value:
                    data['value'] = dict()
                    queryset = ExperimentHasIntron.objects.filter(exp__id=int(value['exp_id']))
                    if 'viewsig' in value and value['viewsig']:
                        if 'pvalue_cutoff' in value:
                            queryset = queryset.filter(pvalue__lte=float(value['pvalue_cutoff']))
                        else:
                            queryset = queryset.filter(pvalue__lte=0.05)
                        if 'fc_cutoff' in value:
                            queryset = queryset.filter(Q(fc__lte=-1.0 * float(value['fc_cutoff'])) | Q(fc__gte=float(value['fc_cutoff'])))
                    if 'r_cutoff' in value:
                        queryset = queryset.filter(
                            Q(r1__gte=float(value['r_cutoff'])) | Q(r2__gte=float(value['r_cutoff'])))
                    if 'xmin' in value:
                        queryset = queryset.filter(fc__gte=float(value['xmin']))
                    if 'xmax' in value:
                        queryset = queryset.filter(fc__lte=float(value['xmax']))
                    if 'ymin' in value:
                        queryset = queryset.filter(pvalue__gte=math.pow(10, -1.0 * float(value['ymin'])))
                    if 'ymax' in value:
                        queryset = queryset.filter(pvalue__lte=math.pow(10, -1.0 * float(value['ymax'])))
                    data['value'] = serializers.serialize('json', queryset.distinct(), fields=(
                        'id', 'exp', 'intron', 'pvalue', 'TPM1', 'TPM2', 'fc', 'r1', 'r2', 'chr', 'gene', 'start',
                        'end'),
                                                          use_natural_foreign_keys=True, use_natural_primary_keys=True)
                    response['success'] = True
    if not response:
        return HttpResponseNotAllowed(['POST'])
    else:
        response['response'] = {
            'operation': data['operation'],
            'property': data['property'],
            'value': data['value']
        }

    return HttpResponse(json.dumps(response), content_type='application/json')


def intron(request, id=False):
    context = {
        'title': 'Intron',
        'current_menu': 'Intron'
    }
    if id:
        intron = ExperimentHasIntron.objects.get(id=id)
        context['intron'] = intron
        context['coord'] = str(intron.start - 100) + ":" + str(intron.end + 100)
    return render(request, 'main/intron.html', context)
