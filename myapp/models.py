from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class User(models.Model):
	usertype=models.CharField(max_length=100,choices=[
		('admin','admin'),
		('member','member')
		],default="member")
	bunglow_no=models.CharField(max_length=100)
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	address=models.TextField()
	password=models.CharField(max_length=100)
	profile_picture=models.ImageField(upload_to='profile_picture/',default="")
	due_amount = models.DecimalField(max_digits=10, decimal_places=2,default='0.00')
	status=models.CharField(max_length=100,default='approved')


	def __str__(self):
		return self.fname + " " +self.bunglow_no+" "+self.usertype

class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	remarks=models.TextField()

	def __str__ (self):
		return self.name



class RegistrationRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(default="pinjal@gmail.com")
    status = models.CharField(max_length=100, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Declined', 'Declined')], default='Pending')
    created_at =models.DateTimeField(auto_now_add=True)
    
    
class Notice(models.Model):
	title=models.CharField(max_length=100)
	notice=models.TextField()

	def __str__(self):
		return self.title


class Member(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    bunglow_no = models.CharField(max_length=100)
    email = models.EmailField(default="")

class PaymentOrder(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')

    def __str__(self):
        return f'Order {self.order_id} - {self.status}'
    
	
class Image(models.Model):
	image=models.ImageField(upload_to='images/')
	uploaded_at=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Image{self.id}'

		