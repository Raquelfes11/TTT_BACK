from django.urls import path
from .views import CategoryListCreate, UserRatingListView,UserBidListView, RatingCreateView, RatingCreateUpdateDelete, CategoryRetrieveUpdateDestroy, AuctionListCreate, AuctionRetrieveUpdateDestroy, BidListCreate, CommentListCreate,CommentRetrieveUpdateDestroy,BidRetrieveUpdateDestroy, UserAuctionListView

app_name = "auctions"
urlpatterns = [
    # CATEGORIAS
    path("categories/", CategoryListCreate.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryRetrieveUpdateDestroy.as_view(), name="category-detail"),

    # SUBASTAS
    path("", AuctionListCreate.as_view(), name="auction-list-create"),
    path("<int:pk>/", AuctionRetrieveUpdateDestroy.as_view(), name="auction-detail"),

    # PUJAS
    path("<int:auction_id>/bids/", BidListCreate.as_view(), name="bid-list-create"),
    path("<int:auction_id>/bids/<int:bid_id>/", BidRetrieveUpdateDestroy.as_view(), name="bid-detail"),

    path('misSubastas/', UserAuctionListView.as_view(), name='user-auctions'),
    path('misPujas/', UserBidListView.as_view(), name='user-bids'),

    # VALORACIONES
    path("<int:auction_id>/ratings/", RatingCreateView.as_view(), name="rating-create"),
    path("<int:auction_id>/ratings/my/", RatingCreateUpdateDelete.as_view(), name="rating-my"),
    path("misValoraciones/", UserRatingListView.as_view(), name="user-ratings"),

    # COMENTARIOS
    path("<int:auction_id>/comments/", CommentListCreate.as_view(), name="comment-list-create"),
    path("<int:auction_id>/comments/<int:comment_id>/", CommentRetrieveUpdateDestroy.as_view(), name="comment-retrieve-update-destroy"),
]