from django.db import models


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        managed = True


class Condition(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    prj = models.ForeignKey(Project)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        managed = True


class Sample(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False, null=False)
    condition = models.ManyToManyField(Condition, related_name='sample')

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        managed = True


class Experiment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    condition1 = models.ForeignKey(Condition, related_name='condition1')
    condition2 = models.ForeignKey(Condition, related_name='condition2')
    TPMRatio_cutoff = models.FloatField()
    pvalue_cutoff = models.FloatField()
    r_cutoff = models.FloatField()

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        managed = True


class Chromosome(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    refseqacc = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        managed = True


class Gene(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    chr = models.ForeignKey(Chromosome)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        managed = True


class Intron(models.Model):
    id = models.AutoField(primary_key=True)
    start = models.IntegerField()
    end = models.IntegerField()
    gene = models.ForeignKey(Gene)

    def __str__(self):
        if self.gene:
            return '%s' % (self.gene.name + ' ' + self.gene.chr.name + ':' + str(self.start) + '-' + str(self.end))
        else:
            return ''

    class Meta:
        managed = True


class ExperimentHasIntron(models.Model):
    id = models.AutoField(primary_key=True)
    exp = models.ForeignKey(Experiment)
    intron = models.ForeignKey(Intron)
    pvalue = models.FloatField()
    TPM1 = models.FloatField()
    TPM2 = models.FloatField()
    fc = models.FloatField()
    r1 = models.FloatField()
    r2 = models.FloatField()
    chr = models.CharField(max_length=255)
    gene = models.CharField(max_length=255)
    start = models.IntegerField()
    end = models.IntegerField()

    def __str__(self):
        if self.exp and self.intron:
            return '%s' % (str(self.exp) + ' ' + str(self.intron))
        else:
            return ''

    class Meta:
        managed = True
