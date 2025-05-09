from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Category, Auction, Bid, Rating
from drf_spectacular.utils import extend_schema_field

class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class AuctionListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)
    auctioneer = serializers.CharField(source='auctioneer.username', read_only=True)

    class Meta:
        model = Auction
        fields = "__all__"

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()
    
    def validate(self, data):
        closing_date = data.get('closing_date')
        creation_date = timezone.now()  

        if closing_date <= creation_date:
            raise serializers.ValidationError("La fecha de cierre no puede ser menor ni igual a la fecha de creación.")

        if closing_date < creation_date + timedelta(days=15):
            raise serializers.ValidationError("La fecha de cierre debe ser al menos 15 días posterior a la fecha de creación.")

        return data

class AuctionBidSerializer(serializers.ModelSerializer):
    bidder_username = serializers.CharField(source='bidder.username', read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'price', 'creation_date', 'bidder_username']
       
class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)
    auctioneer = serializers.CharField(source='auctioneer.username', read_only=True)
    bids = AuctionBidSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = "__all__"
    
    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()

    def get_average_rating(self, obj):
        return obj.average_rating

class BidListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    bidder_username = serializers.CharField(source='bidder.username', read_only=True)
    auction_title = serializers.CharField(source='auction.title', read_only=True)
    auction_thumbnail = serializers.URLField(source='auction.thumbnail', read_only=True)
    auction_id = serializers.IntegerField(source='auction.id', read_only=True)

    class Meta:
        model = Bid
        fields = "__all__"
        read_only_fields = ["id", "creation_date", "auction"]

class BidDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    bidder_username = serializers.CharField(source='bidder.username', read_only=True)
    auction_title = serializers.CharField(source='auction.title', read_only=True)
    auction_thumbnail = serializers.URLField(source='auction.thumbnail', read_only=True)

    class Meta:
        model = Bid
        fields = "__all__"
        read_only_fields = ["id", "creation_date", "auction"]

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id","rating","user","auction"]
        read_only_fields = ["user","auction"]