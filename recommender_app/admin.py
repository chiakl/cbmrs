from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MovieData, CustomUser, MovieData, FinGen, Csr, Final, Admin, Courses, Preference, Subjects, MovieLover, Attendance, AttendanceReport, LeaveReportMovieLover, FeedBackMovieLover, NotificationMovieLover

# Register your models here.
class UserModel(UserAdmin):
    pass


admin.site.register(CustomUser, UserModel)

admin.site.register(Admin)
admin.site.register(Courses)
admin.site.register(Subjects)
admin.site.register(MovieData)
admin.site.register(Preference)
admin.site.register(MovieLover)
admin.site.register(FinGen)
admin.site.register(Attendance)
admin.site.register(Csr)
admin.site.register(Final)
admin.site.register(AttendanceReport)
admin.site.register(LeaveReportMovieLover)
admin.site.register(FeedBackMovieLover)
admin.site.register(NotificationMovieLover)
