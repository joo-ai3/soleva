from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

# Create router for viewsets
router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, basename='addresses')

urlpatterns = [
    # User profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('stats/', views.UserStatsView.as_view(), name='stats'),
    path('preferences/', views.UserPreferencesView.as_view(), name='preferences'),
    path('activity/', views.user_activity, name='activity'),
    
    # Account management
    path('delete/', views.delete_account, name='delete_account'),
    path('export/', views.export_user_data, name='export_data'),
    
    # User search (admin)
    path('search/', views.UserSearchView.as_view(), name='user_search'),
    
    # Include router URLs (addresses)
    path('', include(router.urls)),
]
