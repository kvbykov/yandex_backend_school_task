from django.db import models


class Unit(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=8)
    price = models.PositiveIntegerField(null=True)

    def __repr__(self):
        return f'{self.type}({self.name}, {self.date}, {self.price})'


class History(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    price = models.PositiveIntegerField(null=True)
    parentId = models.UUIDField(null=True)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)

    def __repr__(self):
        return f'History({self.name}, {self.date}, {self.price}, {self.parentId})'