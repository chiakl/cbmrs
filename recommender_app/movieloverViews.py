import string
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.template import RequestContext #To upload Profile Picture
from django.urls import reverse
from .filters import MovieFilter
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import random
import datetime
import csv
from ast import literal_eval
from scipy.sparse import csr_matrix
import numpy as np
from django.template.loader import render_to_string
from django.db.models import Q
import sqlite3
from operator import itemgetter
from pyparsing import empty, quotedString # To Parse input DateTime into Python Date Time Object

from recommender_app.models import MovieData, CustomUser, MovieLover, Csr, Final, FinGen, Preference, Courses, Subjects, Attendance, AttendanceReport, LeaveReportMovieLover, FeedBackMovieLover, MovieLoverResult


def movielover_home(request):
    student_obj = MovieLover.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()

    course_obj = Courses.objects.get(id=student_obj.course_id.id)
    total_subjects = Subjects.objects.filter(course_id=course_obj).count()

    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, student_id=student_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    random_rec = []
    
    pool= list( MovieData.objects.all() )
    random.shuffle( pool )
    random_rec = pool[:5]
    #random_rec = MovieData.objects.order_by('?').first()
    context={
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "total_subjects": total_subjects,
        "subject_name": subject_name,
        "data_present": data_present,
        "data_absent": data_absent,
        "random_rec": random_rec,
    }
    return render(request, "movielover_template/movielover_home_template.html", context)


def movielover_view_attendance(request):
    student = MovieLover.objects.get(admin=request.user.id) # Getting Logged in Student Data
    course = student.course_id # Getting Course Enrolled of LoggedIn Student
    # course = Courses.objects.get(id=student.course_id.id) # Getting Course Enrolled of LoggedIn Student
    subjects = Subjects.objects.filter(course_id=course) # Getting the Subjects of Course Enrolled
    context = {
        "subjects": subjects
    }
    return render(request, "msovielover_template/movielover_view_attendance.html", context)


def movielover_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('movielover_view_attendance')
    else:
        # Getting all the Input Data
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
        subject_obj = Subjects.objects.get(id=subject_id)
        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)
        # Getting Student Data Based on Logged in Data
        stud_obj = MovieLover.objects.get(admin=user_obj)

        # Now Accessing Attendance Data based on the Range of Date Selected and Subject Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), subject_id=subject_obj)
        # Getting Attendance Report based on the attendance details obtained above
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)

        # for attendance_report in attendance_reports:
        #     print("Date: "+ str(attendance_report.attendance_id.attendance_date), "Status: "+ str(attendance_report.status))

        # messages.success(request, "Attendacne View Success")

        context = {
            "subject_obj": subject_obj,
            "attendance_reports": attendance_reports
        }

        return render(request, 'movielover_template/movielover_attendance_data.html', context)
       

def movielover_apply_leave(request):
    student_obj = MovieLover.objects.get(admin=request.user.id)
    leave_data = LeaveReportMovieLover.objects.filter(student_id=student_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, 'movielover_template/movielover_apply_leave.html', context)


def movielover_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('movielover_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        student_obj = MovieLover.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportMovieLover(student_id=student_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('movielover_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('movielover_apply_leave')


def movielover_feedback(request):
    student_obj = MovieLover.objects.get(admin=request.user.id)
    feedback_data = FeedBackMovieLover.objects.filter(student_id=student_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'movielover_template/movielover_feedback.html', context)


def movielover_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('movielover_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        student_obj = MovieLover.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackMovieLover(student_id=student_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('movielover_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('movielover_feedback')


def movielover_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = MovieLover.objects.get(admin=user)

    context={
        "user": user,
        "student": student
    }
    return render(request, 'movielover_template/movielover_profile.html', context)


def movielover_profile_update(request): ######### DONE #########
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('movielover_profile')
    else:
        password = request.POST.get('password')
        #username = request.POST.get('username')
        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            #if username != None and username != "":
            #    customuser.set_username(username)
            #customuser.save()

            student = MovieLover.objects.get(admin=customuser.id)
            student.save()
            
            messages.success(request, "Profile Updated Successfully")
            return redirect('movielover_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('movielover_profile')


def movielover_view_result(request):
    student = MovieLover.objects.get(admin=request.user.id)
    student_result = MovieLoverResult.objects.filter(student_id=student.id)
    context = {
        "student_result": student_result,
    }
    return render(request, "movie_template/movielover_view_result.html", context)

def movielover_movie_list(request): ######### DONE #########
    movie = MovieData.objects.all()
    
    context = {
        "movie": movie, 
    }

    if request.method == 'POST':
        searchMovie = request.POST.get('search')
        genres = ['adventure', 'animation', 'children', 'comedy', 'crime', 'documentary', 'drama', 'fantasy',
                  'film-noir', 'horror', 'musical', 'mystery', 'romance', 'sci-fi', 'thriller']
        if searchMovie.lower() in genres:
            filtered = MovieData.objects.filter(genres__contains=searchMovie, title__contains=searchMovie)
        else:
            filtered = MovieData.objects.filter(title__contains=searchMovie)
        context={
            'movie': filtered
        }
        return render(request, 'movielover_template/movielover_movielist_template.html',context)
    else:
        context = {
        "movie": movie, 
    }          
    return render(request, 'movielover_template/movielover_movielist_template.html',context)


def movielover_preference(request): ######### DONE #########
    user = CustomUser.objects.get(id=request.user.id)
    student = MovieLover.objects.get(admin=user)
    context = {
        "user": user,
        "student": student,
    }
    return render(request, 'movielover_template/movielover_preference.html', context)



def movielover_preference_update(request): ######### DONE #########
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('movielover_preference')
    else:
        pref = request.POST.getlist('pref')
        string = ", ".join(pref)
        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            student = MovieLover.objects.get(admin=customuser.id)
            if pref != None and pref != "":
                student.preference = ''
                student.preference = string
            student.save()
            
            messages.success(request, "Preference(s) Updated Successfully!")
            return redirect('movielover_preference')
        except:
            messages.error(request, "Failed to Update Preference(s)!")
            return redirect('movielover_preference')


def movielover_rec_name(request): ######### DONE #########
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return render(request, 'movielover_template/movielover_rec_name.html')
    else:
        searchMovie = request.POST.get('search')

        db = sqlite3.connect('db.sqlite3')
        m = pd.read_sql_query("SELECT * FROM recommender_app_moviedata", db)
        r = pd.read_sql_query("SELECT * FROM recommender_app_ratings", db)
        f = r.pivot(index='movieId',columns='userId',values='rating')
        f.fillna(0,inplace=True)

        no_user_voted = r.groupby('movieId')['rating'].agg('count')
        no_movies_voted = r.groupby('userId')['rating'].agg('count')

        f = f.loc[no_user_voted[no_user_voted > 10].index,:]
        f = f.loc[:,no_movies_voted[no_movies_voted > 50].index]

        csr_data = csr_matrix(f.values)
        f.reset_index(inplace=True)

        knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
        # brute-force search | distance metric used | -1 means use all processors
        knn.fit(csr_data)

        n_movies_to_reccomend = 10
        movie_list = m[m['title'].str.contains(searchMovie)] 
        if movie_list.size != 0:
            movie_idx = movie_list.iloc[0]['id']
            movie_idx = f[f['movieId'] == movie_idx].index[0]
            distances , indices = knn.kneighbors(csr_data[movie_idx],n_neighbors=n_movies_to_reccomend+1)    
            rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(),distances.squeeze().tolist())),key=lambda x: x[1])[:0:-1]
            recommend_frame = []
            for val in rec_movie_indices:
                movie_idx = f.iloc[val[0]]['movieId']
                idx = m[m['id'] == movie_idx].index
                recommend_frame.append({'Title':m.iloc[idx]['title'].values[0]}) #,'Distance':val[1]})
            df = pd.DataFrame(recommend_frame,index=range(1,n_movies_to_reccomend+1))
            df = df.values.tolist()
            context = {
                'df' : df,
            }
            return render(request, 'movielover_template/movielover_rec_name.html', context)
        else:
            context = {
                'df' : ['No relevant movie was found. Please ensure you enter a valid movie name!']
            }
            return render(request, 'movielover_template/movielover_rec_name.html', context)
        

def movielover_rec_genre(request): ######### DONE #########

    if request.method == 'POST':
        searchMovie = request.POST.get('genreselect') 
        
        db = sqlite3.connect('db.sqlite3')
        fingen = pd.read_sql_query("SELECT * FROM movies_metadata", db)
        fingen.drop(['belongs_to_collection', 'budget', 'homepage', 'original_language', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'video', 'poster_path', 'production_companies', 'production_countries'], axis = 1)
        fingen['genres'] = fingen['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
       
        #vote_count
        V = fingen[fingen['vote_count'].notnull()]['vote_count'].astype('float')
        #vote_average
        R = fingen[fingen['vote_average'].notnull()]['vote_average'].astype('float')
        #vote_average_mean
        C = R.mean()
        #minimum votes required to get in list
        M = V.quantile(0.95)
        
        df_w = pd.DataFrame()
        df_w = fingen[(fingen['vote_count'] >= M) & (fingen['vote_average'].notnull())][['title','vote_count','vote_average','popularity','genres','overview']]
        
        df_w['Weighted_average'] = ((R*V) + (C*M))/(V+M)
        r1 = df_w.sort_values('Weighted_average', ascending=False).head(500)

        p = pd.DataFrame()
        p = r1.copy()
        p['popularity'] = r1[r1['popularity'].notnull()]['popularity'].astype('float')
        p = p.sort_values('popularity',ascending = False)

        s = df_w.apply(lambda x: pd.Series(x['genres']),axis=1).stack().reset_index(level=1, drop=True)
        s.name = 'genre'
        gen_movies = r1.drop('genres', axis=1).join(s)

        df_w = gen_movies[(gen_movies['genre'] == searchMovie) & (gen_movies['vote_count'] >= M)]
        df_w = df_w.sort_values('Weighted_average', ascending = False).head(10)
        df = df_w.drop(['overview', 'vote_count', 'vote_average', 'popularity', 'Weighted_average', 'genre'], axis = 1)
        df = pd.DataFrame(df)
        df = df.values.tolist()
        
        context={
            'rec': df,
            'gen': searchMovie,
        }
        return render(request, 'movielover_template/movielover_rec_genre.html', context)
    else:
        context = {
        #"movie": movie, 
    }          
    return render(request, 'movielover_template/movielover_rec_genre.html') #,context)



def movielover_rec(request): 
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return render(request, 'movielover_template/movielover_rec.html')
    else:
        searchMovie = request.POST.get('search')

        db = sqlite3.connect('db.sqlite3') # by name
        m = pd.read_sql_query("SELECT * FROM recommender_app_moviedata", db)
        r = pd.read_sql_query("SELECT * FROM recommender_app_ratings", db)
        f = r.pivot(index='movieId',columns='userId',values='rating')
        f.fillna(0,inplace=True)

        no_user_voted = r.groupby('movieId')['rating'].agg('count')
        no_movies_voted = r.groupby('userId')['rating'].agg('count')

        f = f.loc[no_user_voted[no_user_voted > 10].index,:]
        f = f.loc[:,no_movies_voted[no_movies_voted > 50].index]

        csr_data = csr_matrix(f.values)
        f.reset_index(inplace=True)

        knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
        knn.fit(csr_data)

        n_movies_to_reccomend = 5
        movie_list = m[m['title'].str.contains(searchMovie)] 
        if movie_list.size != 0:
            movie_idx = movie_list.iloc[0]['id']
            movie_idx = f[f['movieId'] == movie_idx].index[0]
            distances , indices = knn.kneighbors(csr_data[movie_idx],n_neighbors=n_movies_to_reccomend+1)    
            rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(),distances.squeeze().tolist())),key=lambda x: x[1])[:0:-1]
            recommend_frame = []
            for val in rec_movie_indices:
                movie_idx = f.iloc[val[0]]['movieId']
                idx = m[m['id'] == movie_idx].index
                recommend_frame.append({'Title':m.iloc[idx]['title'].values[0],'Distance':val[1]})
            dfn = pd.DataFrame(recommend_frame,index=range(1,n_movies_to_reccomend+1))
            dfn = dfn.values.tolist()

        u = pd.read_sql_query("SELECT preference FROM recommender_app_movielover WHERE id == '1'", db)
        u = u['preference'].iat[0]
        up = u.split(',')[0]
        fingen = pd.read_sql_query("SELECT * FROM movies_metadata", db) # by genre
        fingen.drop(['belongs_to_collection', 'budget', 'homepage', 'original_language', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'video', 'poster_path', 'production_companies', 'production_countries'], axis = 1)
        fingen['genres'] = fingen['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
       
        V = fingen[fingen['vote_count'].notnull()]['vote_count'].astype('float')
        R = fingen[fingen['vote_average'].notnull()]['vote_average'].astype('float')
        C = R.mean()
        M = V.quantile(0.95)
        
        df_w = pd.DataFrame()
        df_w = fingen[(fingen['vote_count'] >= M) & (fingen['vote_average'].notnull())][['title','vote_count','vote_average','popularity','genres','overview']]
        
        df_w['Weighted_average'] = (((R*V) + (C*M))/(V+M)) / 10
        r1 = df_w.sort_values('Weighted_average', ascending=False).head(500)

        p = pd.DataFrame()
        p = r1.copy()
        p['popularity'] = r1[r1['popularity'].notnull()]['popularity'].astype('float')
        p = p.sort_values('popularity',ascending = False)

        s = df_w.apply(lambda x: pd.Series(x['genres']),axis=1).stack().reset_index(level=1, drop=True)
        s.name = 'genre'
        gen_movies = r1.drop('genres', axis=1).join(s)

        df_w = gen_movies[(gen_movies['genre'] == up) & (gen_movies['vote_count'] >= M)]
        df_w = df_w.sort_values('Weighted_average', ascending = False).head(5)
        df = df_w.drop(['overview', 'vote_count', 'vote_average', 'popularity', 'genre'], axis = 1)
        df = pd.DataFrame(df)
        dfg = df.values.tolist()

        res = dfg + dfn
        res = sorted(res, key=itemgetter(1), reverse = True)
        
        context={
            'r': res,
        }
        return render(request, 'movielover_template/movielover_rec.html', context)
