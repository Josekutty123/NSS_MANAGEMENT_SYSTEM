from django.db import models

class UserTab(models.Model):
    id = models.AutoField(primary_key=True)
    regno = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    year = models.IntegerField()
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50) # volunteer, nssleader, admin
    join_date = models.DateField()
    address = models.TextField()
    status = models.CharField(max_length=50) # pending, approved

    class Meta:
        managed = True
        db_table = 'user_tab'


class BloodBank(models.Model):
    id = models.AutoField(primary_key=True)
    regno = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    blood_group = models.CharField(max_length=10)
    phone = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = True
        db_table = 'blood_bank'

    def __str__(self):
        return f"{self.name} ({self.blood_group})"

class PledgeCertificate(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50) # volunteer, nssleader
    pledge_text = models.TextField()
    pledge_date = models.DateField()
    certificate_code = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'pledge_certificate'

    def __str__(self):
        return f"{self.name} - {self.certificate_code}"

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    event_day = models.CharField(max_length=50)
    event_time = models.TimeField()
    place = models.CharField(max_length=255)
    created_by = models.ForeignKey(UserTab, on_delete=models.CASCADE, db_column='created_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'event'

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    sender_role = models.CharField(max_length=50) # admin, nssleader
    sender_id = models.ForeignKey(UserTab, on_delete=models.CASCADE, db_column='sender_id')
    target_role = models.CharField(max_length=50) # volunteer, nssleader, all
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'notification'

