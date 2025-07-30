from django.db import models
from django.conf import settings
from django.utils import timezone

from django.contrib.auth.models import AbstractUser, Group, Permission
# Option 1: Extend User with Profile
from django.contrib.auth.models import User
from django.db import models
class User(AbstractUser):
    USER_ROLES = (
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('tutor', 'Tutor'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLES)
    # etc.

class Admission(models.Model):
    CLASS_CHOICES = [
        ('9th', '9th'),
        ('10th', '10th'),
        ('11th', '11th'),
        ('12th', '12th'),
    ]

    COURSE_CHOICES = [
        ('Biomaths', 'Biomaths'),
        ('Computer Science', 'Computer Science'),
        ('Arts', 'Arts'),
        ('Pure Science', 'Pure Science'),
        ('Commerce', 'Commerce'),
    ]

    Name = models.CharField(max_length=100)
    DOB = models.DateField(verbose_name="Date of Birth")
    Class = models.CharField(max_length=10, choices=CLASS_CHOICES)
    Course = models.CharField(max_length=50, choices=COURSE_CHOICES, blank=True, null=True)
    MotherName = models.CharField(max_length=100)
    FatherName = models.CharField(max_length=100)
    SchoolName = models.CharField(max_length=200)
    Address = models.TextField()
    Number = models.CharField(max_length=10)
    Email = models.EmailField(blank=True, null=True)
    termsCheck = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.Name} ({self.Class})"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    phone= models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Contact from {self.name} ({self.email})  {self.phone})"
    

class Tutor(models.Model):
    Name= models.CharField(max_length=100)
    Subject=models.CharField(max_length=100)
    DOB=models.DateField(verbose_name="Date of Birth",default=timezone.now)
    Age=models.PositiveIntegerField(default=0)
    Gender=models.CharField(max_length=10, choices=[
        ('male','Male'),
        ('female','Female'),
    ],default='other')
    Email=models.EmailField()
    PhoneNumber=models.CharField(max_length=15)
    UserId = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_profile')
    TutorPhoto= models.ImageField(upload_to='tutor_photos/', blank=True, null=True)
    AssignedClass = models.CharField(max_length=50, default='Not Assigned')

    
    def __str__(self):
        return f"{self.UserId.username} - Tutor"
    
from django.db import models
from django.conf import settings

class Student(models.Model):
    CLASS_CHOICES = [
        ('9th', '9th'), 
        ('10th', '10th'),
        ('11th', '11th'),
        ('12th', '12th'),
    ]

    GROUP_CHOICES = [
        ('Biomaths', 'Biomaths'),
        ('Computer Science', 'Computer Science'),
        ('Arts', 'Arts'),
        ('Pure Science', 'Pure Science'),
    ]

    Name = models.CharField(max_length=100)
    DOB = models.DateField(verbose_name="Date of Birth")
    Age = models.PositiveIntegerField()
    Gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ])
    Class = models.CharField(max_length=10, choices=CLASS_CHOICES)
    Group = models.CharField(max_length=50, choices=GROUP_CHOICES, blank=True, null=True)
    SchoolName = models.CharField(max_length=200)
    Email = models.EmailField(blank=True, null=True)
    PhoneNumber = models.CharField(max_length=15)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student')
    StudentPhoto= models.ImageField(upload_to='student_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Student"
    
class Parent(models.Model):
    CLASS_CHOICES = [
        ('9th', '9th'), 
        ('10th', '10th'),
        ('11th', '11th'),
        ('12th', '12th'),
    ]

    GROUP_CHOICES = [
        ('Biomaths', 'Biomaths'),
        ('Computer Science', 'Computer Science'),
        ('Arts', 'Arts'),
        ('Pure Science', 'Pure Science'),
    ]

    Name = models.CharField(max_length=100)
    DOB = models.DateField(verbose_name="Date of Birth")
    Age = models.PositiveIntegerField()
    Gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ])
    Class = models.CharField(max_length=10, choices=CLASS_CHOICES)
    Group = models.CharField(max_length=50, choices=GROUP_CHOICES, blank=True, null=True)
    SchoolName = models.CharField(max_length=200)
    Email = models.EmailField(blank=True, null=True)
    PhoneNumber = models.CharField(max_length=15)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent')
    StudentPhoto= models.ImageField(upload_to='student_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - parent"

    

    

from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Feedback from {self.user.username}'
# Remove redundant models and keep only these:
class TestMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=100,db_index=True)
    subject = models.CharField(max_length=100,db_index=True)
    mark = models.FloatField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['student', 'test_name', 'subject']
        indexes = [
            models.Index(fields=['student', 'test_name', 'subject']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.student.Name} - {self.test_name} - {self.subject}: {self.mark}"

