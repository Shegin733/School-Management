from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeesHistoryViewSet
from admin_dashboard.views import UserProfileView,UpdateUserProfileView,UserViewSet
from librarian_dashboard.views import LibraryHistoryViewSet
router = DefaultRouter()
# router.register('fees-history', views.FeesHistoryViewSet, basename='fees_history')
from common.views import StudentViewSet
urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/<int:id>/', UpdateUserProfileView.as_view(), name='update_user'),
    path('update-user/<int:pk>/', UserViewSet.as_view({'put': 'update_user'}), name='update-user'),
    path('student/create/', StudentViewSet.as_view({'post': 'create'}), name='student-create'),  # Custom URL for create
    path('student/retrieve/<int:pk>/', StudentViewSet.as_view({'get': 'retrieve'}), name='student-retrieve'),  # Custom URL for retrieve
    path('student/update/<int:pk>/', StudentViewSet.as_view({'put': 'update'}), name='student-update'),  # Custom URL for update
    path('student/delete/<int:pk>/', StudentViewSet.as_view({'delete': 'destroy'}), name='student-delete'),  # Custom URL for delete
    path('students/retrieveall/', StudentViewSet.as_view({'get': 'list'}), name='retrieve-all-students'), 
    path('student/<int:student_id>/libraryhistory-view/', LibraryHistoryViewSet.as_view({'get': 'retrieve_by_student'})),
    path('student/<int:student_id>/libraryhistory-view/<int:history_id>/', LibraryHistoryViewSet.as_view({'get': 'retrieve_by_history_and_student'})),
    path('student/libraryhistory-view-history/', LibraryHistoryViewSet.as_view({'get': 'view_history'}), name='libraryhistory-view-history'), # Custom action to view all library history records
    path('student/<int:student_id>/feehistory-create/', FeesHistoryViewSet.as_view({'post': 'create'}), name='feeshistory-create'),
    path('student/<int:student_id>/feehistory-view/', FeesHistoryViewSet.as_view({'get': 'retrieve_by_student'})),
    path('student/<int:student_id>/feehistory-update/<int:pk>/', FeesHistoryViewSet.as_view({'put': 'update'}), name='feeshistory-update'), # Update a specific library history record by ID,
    path('student/<int:student_id>/feehistory-delete/<int:pk>/', FeesHistoryViewSet.as_view({'delete': 'destroy'}), name='feeshistory-delete'),# Delete a specific library history record by ID,
    path('student/<int:student_id>/feehistory-update-status/<int:pk>/', FeesHistoryViewSet.as_view({'patch': 'update_status'}), name='feeshistory-update-status'), # Custom action for updating the status of a library history record
    path('student/feehistory-view-history/', FeesHistoryViewSet.as_view({'get': 'list'}), name='feeshistory-view-history'), # Custom action to view all library history records

]
