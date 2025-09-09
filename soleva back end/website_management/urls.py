from django.urls import path
from . import views

app_name = 'website_management'

urlpatterns = [
    # Admin URLs
    path('admin/sections/', views.WebsiteSectionListCreateView.as_view(), name='admin_sections'),
    path('admin/sections/<uuid:pk>/', views.WebsiteSectionDetailView.as_view(), name='admin_section_detail'),
    path('admin/config/', views.SiteConfigurationView.as_view(), name='admin_site_config'),
    path('admin/banners/', views.NotificationBannerListCreateView.as_view(), name='admin_banners'),
    path('admin/banners/<uuid:pk>/', views.NotificationBannerDetailView.as_view(), name='admin_banner_detail'),
    path('admin/messages/', views.UserMessageListView.as_view(), name='admin_messages'),
    path('admin/messages/create/', views.UserMessageCreateView.as_view(), name='admin_message_create'),
    path('admin/messages/<uuid:pk>/', views.UserMessageDetailView.as_view(), name='admin_message_detail'),
    path('admin/messages/bulk-send/', views.bulk_send_message, name='admin_bulk_message'),
    
    # Public URLs (for frontend)
    path('sections/', views.website_sections_public, name='public_sections'),
    path('config/', views.site_configuration_public, name='public_config'),
    path('banners/', views.notification_banners_public, name='public_banners'),
    
    # User URLs (authenticated users)
    path('user/messages/', views.UserMessagesView.as_view(), name='user_messages'),
    path('user/messages/<uuid:pk>/', views.UserMessageDetailView.as_view(), name='user_message_detail'),
    path('user/messages/<uuid:message_id>/mark-read/', views.mark_message_as_read, name='mark_message_read'),
    path('user/messages/unread-count/', views.unread_messages_count, name='unread_messages_count'),
]
