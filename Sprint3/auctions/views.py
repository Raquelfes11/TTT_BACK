from rest_framework import generics
from .models import Category, Auction, Bid
from .serializers import AuctionDetailSerializer, AuctionListCreateSerializer, CategoryDetailSerializer, CategoryListCreateSerializer, BidDetailSerializer, BidListCreateSerializer
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

# Create your views here.
class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer

class AuctionListCreate(generics.ListCreateAPIView):
    serializer_class = AuctionListCreateSerializer

    def get_queryset(self):
        queryset = Auction.objects.all()

        texto = self.request.query_params.get('texto')
        if texto:
            queryset = queryset.filter(Q(title__icontains=texto) | Q(description__icontains=texto))

        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(category__name__icontains=categoria)  # o `category__id=int(categoria)`

        precio_min = self.request.query_params.get('precioMin')
        precio_max = self.request.query_params.get('precioMax')

        if precio_min:
            queryset = queryset.filter(price__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(price__lte=precio_max)

        is_open = self.request.query_params.get('isOpen')
        if is_open is not None:
            if is_open.lower() == 'true':
                queryset = queryset.filter(closing_date__gt=timezone.now())
            elif is_open.lower() == 'false':
                queryset = queryset.filter(closing_date__lte=timezone.now())


        return queryset

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer

class BidListCreate(generics.ListCreateAPIView):
    serializer_class = BidListCreateSerializer

    def get_queryset(self):
        auction_id = self.kwargs["auction_id"]
        return Bid.objects.filter(auction_id=auction_id)

    def perform_create(self, serializer):
        auction_id = self.kwargs["auction_id"]
        auction = Auction.objects.get(pk=auction_id)

        if auction.closing_date <= timezone.now():
            raise serializers.ValidationError("La subasta ya está cerrada. No se pueden hacer más pujas.")

        serializer.save(auction=auction)


class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidDetailSerializer
    lookup_url_kwarg = "bid_id"

    def get_queryset(self):
        auction_id = self.kwargs["auction_id"]
        return Bid.objects.filter(auction_id=auction_id)


