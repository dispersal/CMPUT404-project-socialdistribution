from rest_framework import views, status
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from .serializers import UserSerializer
from .serializers import PostSerializer
from django.http import Http404
from .models import User, Post, Category, Viewer
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.urls import reverse
from .pagination import CustomPagination
from django.db import transaction


class UserView(views.APIView):

    def get_user(self, user):
        try:
            return User.objects.get(pk=user.pk)
        except:
            raise Http404

    def post(self, request):
        serializer = UserSerializer(data=request.data, context={'create': True})
        if serializer.is_valid() and request.user.is_anonymous:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = self.get_user(request.user)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @method_decorator(login_required)
    def put(self, request):
        user = self.get_user(request.user)
        serializer = UserSerializer(user, data=request.data, partial=True, context={'create':False})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewID(views.APIView):
    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    # TODO: (<AUTHENTICATION>, <VISIBILITY>) check VISIBILITY before getting
    def get(self, request, pk):
        user = self.get_user(pk)
        serializer = UserSerializer(user, context={'request':request})
        return Response(serializer.data)


class AdminUserView(TemplateView):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        unapproved = User.objects.filter(approved=False)

        return render(request, 'users/approve_user.html', context={'unapproved': unapproved})

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_staff:
            raise PermissionDenied
        user_to_approve = request.POST['user']
        user = User.objects.get(id=user_to_approve)
        user.approved = True
        user.save()
        unapproved = User.objects.filter(approved=False)

        return render(request, 'users/approve_user.html', context={'unapproved': unapproved})


# TODO: (<AUTHENTICATION>) Make sure author is approved

class PostView(views.APIView):
    @method_decorator(login_required)
    def post(self, request):
        """
        Create new categories
        """
        if not request.user.approved:
            raise PermissionDenied

        # handle form data for categories
        if type(request.data) is dict:
            categories = request.data.get("categories")
            visibleTo = request.data.get("visibleTo")
        else:
            categories = request.data.getlist("categories")
            visibleTo = request.data.getlist("visibleTo")

        try:
            with transaction.atomic():
                if categories is not None:
                    # author has defined categories
                    for cat in categories:
                        cat_obj = Category.objects.get_or_create(category=cat)
                serializer = PostSerializer(data=request.data, context={'user': request.user})
                if serializer.is_valid():
                    post = serializer.save()
                else:
                    raise ValidationError
                if visibleTo is not None:
                    # author has defined visibleTo
                    for viewer in visibleTo:
                        Viewer.objects.get_or_create(url=viewer, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # TODO: (<AUTHENTICATION>, <VISIBILITY>) check VISIBILITY before getting
    @method_decorator(login_required)
    def get(self, request):
        paginator = CustomPagination()
        # Since we will not be using our api going to use the preferences as a determiner for this.
        serve_other_servers = preferences.SitePreferences.serve_others_posts
        if not serve_other_servers:
            raise PermissionDenied
        serve_images = preferences.SitePreferences.serve_others_images
        if serve_images:
            posts = Post.objects.all().order_by("-published")
        else:
            posts = Post.objects.exclude(contentType__in=['img/png;base64', 'image/jpeg;base64'])

        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data, "posts")


class PostCreateView(TemplateView):
    @method_decorator(login_required)
    def get(self, request):
        serializer = PostSerializer()
        return render(request, "makepost/make-post.html", context={"serializer": serializer})


class FrontEndUserEditView(TemplateView):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        user_data = serializer.data
        github_url = user_data['github']
        github_username = github_url.split('/')[-1]
        return render(request, 'users/edit_user.html', context={'user': serializer.data, 'github_username':github_username})


    @method_decorator(login_required)
    def post(self, request):

        user = request.user
        request_serializer = UserSerializer(user)
        update = (request.POST).dict()
        for attribute, value in update.items():
            if value != "":
                setattr(user, attribute, value)
        try:
            user.save()
        except:
            github_url = request_serializer.data['github']
            github_username = github_url.split('/')[-1]
            return render(request, 'users/edit_user.html', \
                context={'user': request_serializer.data, 'github_username':github_username,
                'error_message':'Error'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user)
        github_url = serializer.data['github']
        github_username = github_url.split('/')[-1]
        return HttpResponseRedirect(reverse('frontauthorposts', args=[user.id]))


class SearchAuthor(views.APIView):
    def get(self, request):
        query = request.GET.get("query", None)
        results = User.objects.filter(username__contains=query)
        serializer = UserSerializer(results, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
