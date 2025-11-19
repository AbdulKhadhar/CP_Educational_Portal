 Educational Portal - Quick Reference Guide

## 🚀 Common Commands

### Project Management
```bash
# Start development server
python manage.py runserver

# Create new app
python manage.py startapp app_name

# Shell access
python manage.py shell

# Database shell
python manage.py dbshell
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name migration_number

# Reset database (CAUTION!)
python manage.py flush
```

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword username
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# Clear static files
python manage.py collectstatic --clear
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test app_name

# Run with coverage
coverage run manage.py test
coverage report
```

## 📊 Model Relationships

### One-to-One
```python
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
```

### Foreign Key (Many-to-One)
```python
class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
```

### Many-to-Many
```python
class PeerGroup(models.Model):
    members = models.ManyToManyField(Student)
```

## 🔍 QuerySet Operations

### Basic Queries
```python
# Get all objects
Student.objects.all()

# Filter
Student.objects.filter(department__name='CSE')

# Get single object
Student.objects.get(roll_number='S2024001')

# Exclude
Student.objects.exclude(current_semester=1)

# Order by
Student.objects.order_by('-admission_year')

# Count
Student.objects.count()
```

### Complex Queries
```python
# Q objects (OR)
from django.db.models import Q
Student.objects.filter(Q(semester=3) | Q(semester=4))

# Aggregation
from django.db.models import Avg, Count, Sum
Student.objects.aggregate(avg_spi=Avg('spi_records__spi_score'))

# Annotation
Student.objects.annotate(course_count=Count('enrollments'))

# Select related (optimize queries)
Student.objects.select_related('department', 'user')

# Prefetch related
Student.objects.prefetch_related('enrollments__section')
```

## 🎨 Template Tags

### Variables
```django
{{ variable }}
{{ object.attribute }}
{{ list.0 }}
```

### Filters
```django
{{ value|date:"M d, Y" }}
{{ text|truncatewords:10 }}
{{ number|floatformat:2 }}
{{ string|upper }}
{{ list|length }}
```

### Tags
```django
{% for item in list %}
    {{ item }}
{% empty %}
    No items
{% endfor %}

{% if condition %}
    ...
{% elif other_condition %}
    ...
{% else %}
    ...
{% endif %}

{% url 'view_name' arg1 arg2 %}

{% static 'path/to/file.css' %}

{% csrf_token %}
```

## 🔐 Authentication

### Login Required
```python
from django.contrib.auth.decorators import login_required

@login_required
def my_view(request):
    pass
```

### Permission Required
```python
from django.contrib.auth.decorators import permission_required

@permission_required('app.permission_name')
def my_view(request):
    pass
```

### User Checks
```python
if request.user.is_authenticated:
    pass

if request.user.is_staff:
    pass

if request.user.has_perm('app.permission'):
    pass
```

## 📝 Form Handling

### Form in View
```python
def my_view(request):
    if request.method == 'POST':
        form = MyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = MyForm()
    return render(request, 'template.html', {'form': form})
```

### Form in Template
```django
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

## 🌐 URL Patterns

### Basic URL
```python
path('path/', view, name='url_name')
```

### With Parameters
```python
path('item/<int:pk>/', view, name='detail')
path('user/<str:username>/', view, name='profile')
```

### Include
```python
path('api/', include('api.urls'))
```

## 📊 Chart.js Integration

### In View
```python
def chart_data(request):
    data = {
        'labels': ['Jan', 'Feb', 'Mar'],
        'data': [10, 20, 30]
    }
    return JsonResponse(data)
```

### In Template
```html
<canvas id="myChart"></canvas>
<script>
fetch('{% url "chart_data" %}')
    .then(response => response.json())
    .then(data => {
        new Chart(document.getElementById('myChart'), {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data
                }]
            }
        });
    });
</script>
```

## 🐛 Debugging Tips

### Print in Template
```django
{{ variable|pprint }}
{{ object|dir }}
```

### Debug in View
```python
import pdb; pdb.set_trace()
print(f"Debug: {variable}")
```

### Enable Debug Toolbar
```python
# settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

## 📦 Useful Packages

```bash
# Django Extensions
pip install django-extensions

# Debug Toolbar
pip install django-debug-toolbar

# REST Framework
pip install djangorestframework

# CORS Headers
pip install django-cors-headers

# Environment Variables
pip install python-decouple

# Image Processing
pip install Pillow

# PDF Generation
pip install reportlab

# Excel Support
pip install openpyxl
```

## 🔧 Common Fixes

### Clear Migrations
```bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```

### Reset Database
```bash
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

### Fix Static Files
```bash
python manage.py collectstatic --clear --noinput
python manage.py collectstatic --noinput
```

## 🎯 Performance Tips

1. **Use select_related() and prefetch_related()**
   ```python
   Student.objects.select_related('department')
   ```

2. **Add database indexes**
   ```python
   class Meta:
       indexes = [models.Index(fields=['roll_number'])]
   ```

3. **Use pagination**
   ```python
   from django.core.paginator import Paginator
   paginator = Paginator(object_list, 25)
   ```

4. **Cache frequently used data**
   ```python
   from django.core.cache import cache
   cache.set('key', value, timeout=300)
   ```

5. **Optimize queries**
   ```python
   # Bad
   for student in students:
       print(student.department.name)
   
   # Good
   students = Student.objects.select_related('department')
   for student in students:
       print(student.department.name)
   ```

## 📱 Bootstrap 5 Classes Quick Reference

### Spacing
```
m-{0-5}  - margin
p-{0-5}  - padding
mt-3     - margin-top: 1rem
px-4     - padding left and right: 1.5rem
```

### Colors
```
bg-primary, bg-success, bg-danger, bg-warning, bg-info
text-primary, text-success, text-muted
```

### Display
```
d-none, d-block, d-flex
d-sm-block, d-md-none
```

### Flex
```
d-flex
justify-content-{start|center|end|between}
align-items-{start|center|end}
```

### Grid
```
<div class="row">
    <div class="col-md-6">Half width on medium+</div>
    <div class="col-md-6">Half width on medium+</div>
</div>
```

---

**Keep this guide handy for quick reference while developing!**