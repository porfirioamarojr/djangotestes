import datetime

from django.shortcuts import render
from catalogo.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
#from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
#from django.views.generic import View
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalogo.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalogo.models import Author

# Create your views here.
def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    return render(request, 'catalogo/book_detail.html', context={'book': book})

def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalogo/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    #context_object_name = 'my_book_list'   # your own name for the list as a template variable
    #queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    #template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location

    #def get_queryset(self):
    #    return Book.objects.filter(title__icontains='war')[:5]
    #
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context        
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model = Book


#class MyView(LoginRequiredMixin, View):
#    login_url = '/login/'
#    redirect_field_name = 'redirect_to'


@permission_required('catalogo.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalogo/book_renew_librarian.html', context)

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
