from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to="profile_pics/",
        default="profile_pics/default.png"
    )

    def __str__(self):
        return self.user.username
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Pridiction(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='pridictions')
    N = models.FloatField() 
    P = models.FloatField() 
    K = models.FloatField() 
    temperature = models.FloatField() 
    humidity = models.FloatField() 
    ph = models.FloatField() 
    rainfall = models.FloatField() 
    predicted_label = models.CharField(max_length=100)
    created_at =models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    
    
    def __str__(self):
        return f'{self.user.username} -> {self.predicted_label}'