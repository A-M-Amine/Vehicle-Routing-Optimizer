from django.db import models
from api.vehicle.models import Vehicle
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


# setting a high value for time (minutes) by default to handle Deliveries with no time window
def default_time_window_dict():
    return [0, 14400]


class Optimizer(models.Model):
    name = models.CharField(max_length=150, unique=True, blank=True, null=True)
    solved = models.BooleanField(default=False)
    depot = models.JSONField()
    vehicles = models.ManyToManyField(Vehicle)
    matrix = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{str(self.id)}  {self.name}, depot index : {self.depot}"


class Delivery(models.Model):
    coordinates = models.JSONField()
    package_size = models.IntegerField(default=-1)
    time_window = models.JSONField(default=default_time_window_dict)

    optimizer = models.ForeignKey(Optimizer, on_delete=models.CASCADE, related_name='deliveries', blank=True, null=True)


# TODO catch error where Delivery count is lower than two
@receiver(post_delete, sender=Delivery)
def update_optimizer_solved(sender, instance, **kwargs):
    # instance is the deleted delivery object
    # get the optimizer related to the delivery
    optimizer = instance.optimizer
    # check if the optimizer has any other deliveries
    optimizer.solved = False
    optimizer.save()


@receiver(pre_save, sender=Delivery)
def update_optimizer_solved(sender, instance, **kwargs):
    # instance is the delivery object that is about to be saved
    # get the optimizer related to the delivery
    optimizer = instance.optimizer
    # check if the delivery already exists in the database
    if instance.pk:
        # get the old delivery object from the database
        old_delivery = Delivery.objects.get(pk=instance.pk)
        # compare fields of old and new delivery objects
        old_delivery = list(vars(old_delivery).values())[2:]
        instance = list(vars(instance).values())[2:]

        for index, item in enumerate(old_delivery):
            if item != instance[index]:
                optimizer.solved = False
                # save the optimizer
                optimizer.save()
