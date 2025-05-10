from rest_framework import generics, serializers
from .models import Category, Auction, Bid, Rating, Comment
from .serializers import AuctionDetailSerializer,CommentSerializer ,AuctionListCreateSerializer, CategoryDetailSerializer, CategoryListCreateSerializer, RatingSerializer, BidDetailSerializer, BidListCreateSerializer
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Q, F, Value, FloatField
from django.db.models.functions import Coalesce
from django.core.exceptions import PermissionDenied
from .permissions import IsOwnerOrAdmin, IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, IsBidderOrAdmin, IsCommentOwnerOrAdmin

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
        valoracion_min = self.request.query_params.get('valoracionMin')

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
        
        if valoracion_min:
            # Anota cada subasta con su rating promedio y filtra
            queryset = queryset.annotate(
                avg_rating=Coalesce(Avg('ratings__rating'), Value(1.0, output_field=FloatField()))
            ).filter(avg_rating__gte=float(valoracion_min))



        return queryset

    def perform_create(self, serializer):
        serializer.save(auctioneer=self.request.user)

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
        return Bid.objects.filter(auction_id=auction_id).order_by('-price')
    
    def perform_create(self, serializer):
        auction_id = self.kwargs["auction_id"]
        auction = Auction.objects.get(pk=auction_id)

        if auction.closing_date <= timezone.now():
            raise serializers.ValidationError("La subasta ya está cerrada. No se pueden hacer más pujas.")

        max_bid = auction.bids.aggregate(models.Max('price'))['price__max'] or 0
        new_price = serializer.validated_data['price']

        if new_price <= max_bid:
            raise serializers.ValidationError("La puja debe ser mayor que cualquier puja existente.")

        serializer.save(auction=auction, bidder=self.request.user)


class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBidderOrAdmin]
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
    
    def delete(self, request, *args, **kwargs):
        # Buscar las subastas del usuario
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        deleted_count = user_auctions.count()

        # Eliminar todas las subastas
        user_auctions.delete()

        return Response({"detail": f"Se eliminaron {deleted_count} subastas."}, status=204)
    
class UserBidListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_bids = Bid.objects.filter(bidder=request.user)
        serializer = BidListCreateSerializer(user_bids, many=True)
        return Response(serializer.data)

class RatingCreateView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        auction_id = self.kwargs["auction_id"]
        if Rating.objects.filter(auction_id=auction_id, user=self.request.user).exists():
            raise serializers.ValidationError("Ya has valorado esta subasta.")
        serializer.save(user=self.request.user, auction_id=auction_id)

class RatingCreateUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        auction_id = self.kwargs["auction_id"]
        rating = get_object_or_404(Rating, auction_id=auction_id, user=self.request.user)
        return rating

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

class CommentListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        auction_id = self.kwargs["auction_id"]
        return Comment.objects.filter(auction_id=auction_id).order_by('-created_at')

    def perform_create(self, serializer):
        auction_id = self.kwargs["auction_id"]
        auction = Auction.objects.get(pk=auction_id)
        serializer.save(user=self.request.user, auction=auction)

class CommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated] HE CAMBIADO ESTO!!
    permission_classes = [IsCommentOwnerOrAdmin]
    serializer_class = CommentSerializer
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        auction_id = self.kwargs["auction_id"]
        return Comment.objects.filter(auction_id=auction_id)

    def get_object(self):
        try:
            return super().get_object()
        except Comment.DoesNotExist:
            raise NotFound("El comentario no fue encontrado.")
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

class UserRatingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_ratings = Rating.objects.filter(user=request.user).select_related('auction', 'auction__category')
        data = []

        for rating in user_ratings:
            auction = rating.auction
            data.append({
                "id": rating.id,
                "rating": rating.rating,
                "auction_title": auction.title,
                "auction_price": auction.price,
                "auction_category": auction.category.name,
                "auction_is_open": auction.closing_date > timezone.now(),
                "auction_thumbnail": auction.thumbnail,
                "auction_id": auction.id
            })

        return Response(data)
    
class UserCommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_comments = Comment.objects.filter(user=request.user).select_related('auction', 'auction__category')
        data = []

        for comment in user_comments:
            print(f"Comentario ID: {comment.id}, Texto: {comment.text}")
            auction = comment.auction
            data.append({
                "id": comment.id,
                "title": comment.title,
                "text": comment.text,
                "created_at": comment.created_at,
                "auction_title": auction.title,
                "auction_price": auction.price,
                "auction_category": auction.category.name,
                "auction_is_open": auction.closing_date > timezone.now(),
                "auction_thumbnail": auction.thumbnail,
                "auction_id": auction.id
            })

        return Response(data)

