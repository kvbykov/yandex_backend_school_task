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


# class Offer(models.Model):
#     id = models.UUIDField(primary_key=True)
#     name = models.CharField(max_length=255)
#     date = models.DateTimeField()
#     price = models.PositiveIntegerField()
#     parentId = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True, default=None)
#
#     def __repr__(self):
#         return f'Offer({self.id}, {self.name})'
#
#
# class Category(models.Model):
#     id = models.UUIDField(primary_key=True)
#     name = models.CharField(max_length=255)
#     date = models.DateTimeField()
#     price = models.PositiveIntegerField(null=True, default=None)
#     parentId = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, default=None)
#
#     def __repr__(self):
#         return f'Category({self.id}, {self.name})'
#
#
class History(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    price = models.PositiveIntegerField(null=True)
    parentId = models.UUIDField(null=True)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)

    def __repr__(self):
        return f'History({self.name}, {self.date}, {self.price}, {self.parentId})'
