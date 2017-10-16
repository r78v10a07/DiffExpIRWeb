from django.contrib import admin

from project.main.models import *


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = ['name', 'description']


admin.site.register(Project, ProjectAdmin)


class ConditionAdmin(admin.ModelAdmin):
    model = Condition
    list_display = ['name', 'description']


admin.site.register(Condition, ConditionAdmin)


class SampleAdmin(admin.ModelAdmin):
    model = Sample
    list_display = ['name']


admin.site.register(Sample, SampleAdmin)


class ExperimentAdmin(admin.ModelAdmin):
    model = Experiment
    list_display = ['name', 'description', 'Condition1', 'Condition2']

    def Condition1(self, obj):
        return obj.condition1.name

    def Condition2(self, obj):
        return obj.condition2.name


admin.site.register(Experiment, ExperimentAdmin)


class ChromosomeAdmin(admin.ModelAdmin):
    model = Chromosome
    list_display = ['name']


admin.site.register(Chromosome, ChromosomeAdmin)


class GeneAdmin(admin.ModelAdmin):
    model = Gene
    list_display = ['name', 'Chr']

    def Chr(self, obj):
        return obj.chr.name


admin.site.register(Gene, GeneAdmin)


class IntronAdmin(admin.ModelAdmin):
    model = Intron
    list_display = ['Gene', 'start', 'end']

    def Gene(self, obj):
        return obj.gene.name


admin.site.register(Intron, IntronAdmin)


class ExperimentHasIntronAdmin(admin.ModelAdmin):
    model = ExperimentHasIntron
    list_display = ['exp', 'intron', 'pvalue', 'TPM1', 'TPM2', 'r1', 'r2']

    def exp(self, obj):
        return obj.exp.name

    def intron(self, obj):
        return str(obj.intron.start) + '-' + str(obj.intron.end)


admin.site.register(ExperimentHasIntron, ExperimentHasIntronAdmin)
