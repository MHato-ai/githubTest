from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    category = models.CharField(max_length=100, null=False, blank=False)
    num_of_products = models.IntegerField()

    def __str__(self):
        return f'{self.category} - {self.num_of_products}'


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'