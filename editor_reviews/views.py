from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Editor_Reviews
from .forms import Editors_Reviews_Form
from users.models import Editor
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    first_review = Editor_Reviews.objects.first()
    review_list = Editor_Reviews.objects.all()[1:]
    editors = Editor.objects.all()
    ctx = {
        'first_review': first_review,
        'review_list': review_list,
        'editors': editors,
    }

    return render(request, 'editor_reviews/editor_reviews_list.html', ctx)


def detail(request, pk):
    review = get_object_or_404(Editor_Reviews, pk=pk)
    ctx = {
        'review': review,
    }
    return render(request, 'editor_reviews/editor_reviews_detail.html', ctx)
# Create your views here.


@login_required
def create(request):
    try:
        user = request.user.editor
    except ObjectDoesNotExist:
        return redirect(reverse('editors_pick:index'))
    
    if request.method == 'POST':
        form = Editors_Reviews_Form(request.POST, request.FILES)
        if form.is_valid():
            print("값이 검증은 되었다")
            editor_review = Editor_Reviews(**(form.cleaned_data))
            editor_review.author = user
            editor_review.save()
            return redirect(reverse("editors_pick:detail editor_review.pk"))
        else:
            print("이것은 무엇이냐")
            return redirect(reverse("core:main"))
    else:
        form = Editors_Reviews_Form()
        ctx = {
            'form': form,
        }
        return render(request, 'editor_reviews/editor_reviews_create.html', ctx)


def update(request, pk):
    post = get_object_or_404(Editor_Reviews, pk=pk)

    if request.method == 'POST':
        form = Editors_Reviews_Form(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('detail', pk)

    else:
        form = Editors_Reviews_Form(instance=post)

    return render(request, 'editors_reviews/update.html', {'forms': form})


def delete(request, pk):

    post = Editor_Reviews.object.get(pk=pk)
    post.delete()

    return redirect('index')
