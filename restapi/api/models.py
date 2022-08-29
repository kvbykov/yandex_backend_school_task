from django.db import models


class Offer(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    price = models.PositiveIntegerField()
    parentId = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True, default=None)

    def __repr__(self):
        return f'Offer({self.id}, {self.name})'


class Category(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    price = models.PositiveIntegerField(null=True, default=None)
    parentId = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, default=None)

    def __repr__(self):
        return f'Category({self.id}, {self.name})'


class History(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    price = models.PositiveIntegerField()
    parentId = models.UUIDField()
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, blank=True, null=True, default=None)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True, default=None)

    def __repr__(self):
        return f'History({self.name}, {self.date}, {self.price}, {self.parentId})'
