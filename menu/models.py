from django.db import models


class MenuItem(models.Model):
    """
    Maps 1:1 to the Flutter app's MenuItemModel (name, description, imageUrl,
    size, price). Admins create/edit these from the Django admin site; the
    Flutter dashboard reads them through the read-only /api/menu/ endpoint.
    """

    name = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    size = models.CharField(max_length=50, help_text='e.g. Medium (12 inch), Regular, 500ml')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True, help_text='Uncheck to hide from the app without deleting it')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
