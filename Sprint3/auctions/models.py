from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)

    class Meta:
        ordering = ("id",)
    
    def __str__(self):
        return self.name
    
class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.IntegerField(validators=[MinValueValidator(1)])
    stock = models.IntegerField(validators=[MinValueValidator(1)])
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name="auctions", on_delete=models.CASCADE)
    thumbnail = models.URLField()
    creation_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField()
    auctioneer = models.ForeignKey(CustomUser, related_name='auctions', on_delete=models.CASCADE)

    @property
    def average_rating(self):
        result = self.ratings.aggregate(avg=models.Avg('rating'))['avg']
        return round(result, 2) if result else 1.0
    
    class Meta:
        ordering = ("id",)
    
    def __str__(self):
        return self.title
    
class Bid(models.Model):
    auction = models.ForeignKey(Auction, related_name="bids", on_delete=models.CASCADE)
    price = models.IntegerField(validators=[MinValueValidator(1)])
    creation_date = models.DateTimeField(auto_now_add=True)
    bidder = models.ForeignKey(CustomUser, related_name="bids", on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)
    
    def __str__(self):
        return f"Puja {self.id} - {self.bidder}"
    
class Rating(models.Model):
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(CustomUser, related_name="ratings",on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name="ratings", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "auction")
        ordering = ("id",)
    
    def __str__(self):
        return f"Rating {self.rating} by {self.user} for {self.auction}"

class Comment(models.Model):
    title = models.CharField(max_length=150)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, related_name="comments", on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name="comments", on_delete=models.CASCADE)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Comentario de {self.user.username} en {self.auction.title}"
