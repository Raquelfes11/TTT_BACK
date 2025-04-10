from rest_framework import generics, serializers
from .models import Category, Auction, Bid
from .serializers import AuctionDetailSerializer, AuctionListCreateSerializer, CategoryDetailSerializer, CategoryListCreateSerializer, BidDetailSerializer, BidListCreateSerializer
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .permissions import IsOwnerOrAdmin, IsAuthenticatedOrReadOnly, IsAdminOrReadOnly

# Create your views here.
class CategoryListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer

class AuctionListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = AuctionListCreateSerializer

    def get_queryset(self):
        queryset = Auction.objects.all()

        texto = self.request.query_params.get('texto',None)
        precio_min = self.request.query_params.get('precioMin', None)
        precio_max = self.request.query_params.get('precioMax', None)
        is_open = self.request.query_params.get('isOpen', None)

        if texto:
            queryset = queryset.filter(Q(title__icontains=texto) | Q(description__icontains=texto))

        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(category__name__icontains=categoria)  # o `category__id=int(categoria)`

        if precio_min:
            queryset = queryset.filter(price__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(price__lte=precio_max)

        if is_open is not None:
            if is_open.lower() == 'true':
                queryset = queryset.filter(closing_date__gt=timezone.now())
            elif is_open.lower() == 'false':
                queryset = queryset.filter(closing_date__lte=timezone.now())


        return queryset

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = AuctionDetailSerializer

    def get_queryset(self):
        return Auction.objects.all()

    def get_object(self):
        try:
            return super().get_object()
        except Auction.DoesNotExist:
            raise NotFound("La subasta no fue encontrada.")

class BidListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
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
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = BidDetailSerializer
    lookup_url_kwarg = "bid_id"

    def get_queryset(self):
        auction_id = self.kwargs["auction_id"]
        return Bid.objects.filter(auction_id=auction_id)

class UserAuctionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
    # Obtener las subastas del usuario autenticado
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionListCreateSerializer(user_auctions, many=True)
        return Response(serializer.data)