from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Изображение")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    composition = models.TextField(verbose_name="Состав", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    weight = models.IntegerField(verbose_name="Вес (г)", default=0)
    pieces = models.IntegerField(verbose_name="Количество кусочков", default=0)
    image = models.ImageField(upload_to='products/', blank=True, verbose_name="Изображение")
    available = models.BooleanField(default=True, verbose_name="Доступен")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        ordering = ['category__order', 'order']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    
    def __str__(self):
        return self.name