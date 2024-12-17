from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .views import  RetrieveRoleProfileView,CreateRoleProfileView,UpdateUserProfileView,RetrieveProfilesView,DeleteProfileView,UserProfileView
#from common.views import StudentCreateView,StudentDeleteView,StudentUpdateView,StudentRetrieveView,RetrieveAllStudentsView
from common.views import StudentViewSet
from librarian_dashboard.views import LibraryHistoryViewSet
from office_staff_dashboard.views import FeesHistoryViewSet
router = DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('create-user/', UserViewSet.as_view({'post': 'create_user'}), name='create-user'),  # Create user
    path('retrieve-user/<int:pk>/', UserViewSet.as_view({'get': 'retrieve_user'}), name='retrieve-user'),  # Retrieve specific user
    path('retrieve-users/', UserViewSet.as_view({'get': 'retrieve_all_users'}), name='retrieve-all-users'),  # Retrieve all users
    path('update-user/<int:pk>/', UserViewSet.as_view({'put': 'update_user'}), name='update-user'),  # Update user
    path('delete-user/<int:pk>/', UserViewSet.as_view({'delete': 'delete_user'}), name='delete-user'),  # Delete user

    path('profiles/<int:user_id>/<str:role>/create/', CreateRoleProfileView.as_view(), name='create_role_profile'),
    path('profile/update/<int:id>/', UpdateUserProfileView.as_view(), name='update_user'),
    path('retrieve-profile/<int:id>/', RetrieveRoleProfileView.as_view(), name='retrieve-user'),
    path('retrieve-profiles/<str:role>/', RetrieveProfilesView.as_view(), name='retrieve-all-profiles'),
    path('delete-profile/<int:id>/', DeleteProfileView.as_view(), name='delete-profile'),

    path('student/create/', StudentViewSet.as_view({'post': 'create'}), name='student-create'),  # Custom URL for create
    path('student/retrieve/<int:pk>/', StudentViewSet.as_view({'get': 'retrieve'}), name='student-retrieve'),  # Custom URL for retrieve
    path('student/update/<int:pk>/', StudentViewSet.as_view({'put': 'update'}), name='student-update'),  # Custom URL for update
    path('student/delete/<int:pk>/', StudentViewSet.as_view({'delete': 'destroy'}), name='student-delete'),  # Custom URL for delete
    path('students/retrieveall/', StudentViewSet.as_view({'get': 'list'}), name='retrieve-all-students'),  # Custom URL for retrieving all students

    path('student/<int:student_id>/library-create/', LibraryHistoryViewSet.as_view({'post': 'create'}), name='libraryhistory-create'),
    path('student/<int:student_id>/libraryhistory-view/', LibraryHistoryViewSet.as_view({'get': 'retrieve_by_student'})),
    path('student/<int:student_id>/libraryhistory-view/<int:history_id>/', LibraryHistoryViewSet.as_view({'get': 'retrieve_by_history_and_student'})),
    path('student/libraryhistory-view-history/', LibraryHistoryViewSet.as_view({'get': 'view_history'}), name='libraryhistory-view-history'), # Custom action to view all library history records
    path('student/<int:student_id>/libraryhistory-update/<int:pk>/', LibraryHistoryViewSet.as_view({'put': 'update'}), name='libraryhistory-update'), # Update a specific library history record by ID,
    path('student/<int:student_id>/libraryhistory-delete/<int:pk>/', LibraryHistoryViewSet.as_view({'delete': 'destroy'}), name='libraryhistory-delete'),# Delete a specific library history record by ID,
    path('student/<int:student_id>/libraryhistory-update-status/<int:pk>/', LibraryHistoryViewSet.as_view({'patch': 'update_status'}), name='libraryhistory-update-status'), # Custom action for updating the status of a library history record
   
    path('student/<int:student_id>/feehistory-create/', FeesHistoryViewSet.as_view({'post': 'create'}), name='feeshistory-create'),
    path('student/<int:student_id>/feehistory-view/', FeesHistoryViewSet.as_view({'get': 'retrieve_by_student'})),
    path('student/<int:student_id>/feehistory-update/<int:pk>/', FeesHistoryViewSet.as_view({'put': 'update'}), name='feeshistory-update'), # Update a specific library history record by ID,
    path('student/<int:student_id>/feehistory-delete/<int:pk>/', FeesHistoryViewSet.as_view({'delete': 'destroy'}), name='feeshistory-delete'),# Delete a specific library history record by ID,
    path('student/<int:student_id>/feehistory-update-status/<int:pk>/', FeesHistoryViewSet.as_view({'patch': 'update_status'}), name='feeshistory-update-status'), # Custom action for updating the status of a library history record
    path('student/feehistory-view-history/', FeesHistoryViewSet.as_view({'get': 'list'}), name='feeshistory-view-history'), # Custom action to view all library history records
]

