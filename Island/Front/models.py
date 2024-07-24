from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)  # کلید اصلی خودکار
    username = models.CharField(max_length=255, unique=True)  # نام کاربری منحصر به فرد
    level = models.IntegerField(default=1)
    friends = models.ManyToManyField('self', blank=True)
    join = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Inventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventories', db_column='user_id')
    tank = models.BooleanField(default=False)
    fullcharge = models.BooleanField(default=False)
    rocket = models.BooleanField(default=False)

    def __str__(self):
        return f"Inventory for {self.user.username}"

class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards', db_column='user_id')
    coins = models.IntegerField(default=0)
    luckywheel = models.BooleanField(default=False)
    check_daily_reward = models.BooleanField(default=False)

    def __str__(self):
        return f"Rewards for {self.user.username}"
