from .models import Inventory

def reset_rocket_inventory():
    inventories = Inventory.objects.all()
    for inventory in inventories:
        inventory.rocket = 3
        inventory.save()