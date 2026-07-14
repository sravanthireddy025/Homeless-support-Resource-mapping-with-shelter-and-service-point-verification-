from django.urls import path
from .views import *

urlpatterns = [

    # AUTH
    path("register/", register_api),
    path("login/", login_api),

    # ADMIN USERS
    path("admin/user/", admin_user_api),
    path("approve/", approve_user_api),

    # SERVICES
    path("service/add/", add_service_api),
    path("services/nearby/", nearby_services_api),
    path("admin/update-service/", update_service_api),
    path("admin/change-service-status/", change_service_status_api),

    # USER BASIC
    path("user/details/", user_details_api),
    path("user/page/", user_page_api),

    # USER FEATURES (NEW)
    path("user/report-issue/", report_issue_api),
    path("user/my-issues/", user_my_issues_api),

    path("user/submit-query/", submit_query_api),
    path("user/my-queries/", user_my_queries_api),

    path("user/rate-service/", rate_service_api),

    # ADMIN FEATURES
    path("admin/issues/", admin_view_issues_api),
    path("admin/resolve-issue/", resolve_issue_api),

    path("admin/queries/", admin_view_queries_api),
    path("admin/reply-query/", reply_query_api),

    path("admin/ratings/", admin_view_ratings_api),
]
