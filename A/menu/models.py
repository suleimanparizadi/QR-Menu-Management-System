from django.db import models
from accounts.models import User
import qrcode
from django.core.files import File
from io import BytesIO
from django.conf import settings


class QRMenu(models.Model):

    """
    Represents a QR-code-enabled menu.

    This model is designed to create and store a QR code for a menu associated with a user. 
    The QR code links to the menu's unique URL. It also stores metadata about the menu, such as 
    its title, description, availability status, and creation date.

    """

    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='menus')
    title = models.CharField(max_length=225)
    description = models.CharField(max_length=350, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_menu/')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
            
        qr_data = f"https://TheWebSiteAddres/menu/{self.id}"
        qr_image = qrcode.make(qr_data)
        qr_io = BytesIO()
        qr_image.save(qr_io, 'PNG')
        self.qr_code.save(f'{self.title}.png', File(qr_io), save=False)
        qr_io.close()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.description} - {self.id}"
    


    def delete(self, *args, **kwargs):

        if self.qr_code and self.qr_code.storage.exists(self.qr_code.name):
            self.qr_code.delete(save=False)
        return super().delete(*args, **kwargs)


class MenuItem(models.Model):

    """
    Represents an item in a QRMenu.

    This model defines a single item in a menu. Each menu item is linked to a parent QRMenu 
    and includes details about the item, such as its name, description, price, and availability status.

    """

    menu = models.ForeignKey(QRMenu, on_delete=models.CASCADE, related_name='items')
    item = models.CharField(max_length=225)
    description = models.CharField(max_length=225)
    price = models.IntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item} - {self.menu} - {self.id}"
