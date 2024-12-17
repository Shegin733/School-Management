from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from common.views import StudentViewSet
from admin_dashboard.views import UserViewSet,UpdateUserProfileView,RetrieveRoleProfileView,UserProfileView
from .views import LibraryHistoryViewSet
router = DefaultRouter()
router.register('library-history', views.LibraryHistoryViewSet, basename='library_history')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/<int:id>/', UpdateUserProfileView.as_view(), name='update_user'),
    path('student/retrieve/<int:pk>/', StudentViewSet.as_view({'get': 'retrieve'}), name='student-retrieve'),  # Custom URL for retrieve
    path('students/retrieveall/', StudentViewSet.as_view({'get': 'list'}), name='retrieve-all-students'),
    # Library History URLs
    path('student/<int:student_id>/libraryhistory-update-status/<int:pk>/', LibraryHistoryViewSet.as_view({'patch': 'update_status'}), name='libraryhistory-update-status'), # Custom action for updating the status of a library history record
    path('student/libraryhistory-view-history/', LibraryHistoryViewSet.as_view({'get': 'view_history'}), name='libraryhistory-view-history'), # Custom action to view all library history records
    path('update-user/<int:pk>/', UserViewSet.as_view({'put': 'update_user'}), name='update-user'),#can update librarian's own profile
   
]
