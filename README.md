# Educational Portal - Django Web Application

A comprehensive college management system built with Django, featuring role-based access control for admins, teachers, and students.

## 🎯 Features

### For College Admins
- Manage departments, courses, and sections
- Register and manage teachers and students
- View comprehensive analytics and reports
- Monitor student participation indexes (SPI)
- Generate certificates and award badges

### For Teachers
- Manage assigned courses and sections
- Upload study materials (PDFs, videos, presentations)
- Create and grade assignments
- Create and manage quizzes with auto-grading
- Mark attendance
- Post announcements
- Participate in discussion forums

### For Students
- Access enrolled courses and materials
- Submit assignments and take quizzes
- View grades, attendance, and SPI
- Participate in discussion forums
- Earn badges and certificates
- Join peer learning groups

## 📊 Key Components

### Student Participation Index (SPI)
```
SPI = (0.4 × Assignment Score) + (0.3 × Quiz Score) + 
      (0.2 × Attendance %) + (0.1 × Forum Activity)
```

### Analytics Dashboard
- Real-time participation metrics
- SPI distribution visualization
- Attendance trends
- At-risk student identification
- Department-wise performance analysis

## 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, Chart.js
- **Authentication**: Django's built-in authentication with custom user model
- **File Handling**: Django's FileField with validation

## 📁 Project Structure

```
educational_portal/
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── educational_portal/          # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                    # User authentication & roles
│   ├── models.py               # Custom User, College
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── colleges/                    # College management
│   ├── models.py               # Department, Course, ClassSection, Teacher, Student
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── courses/                     # Course materials & assignments
│   ├── models.py               # StudyMaterial, Assignment, Submission, Attendance
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── quizzes/                     # Quiz system
│   ├── models.py               # Quiz, QuizQuestion, QuizAttempt, QuizResult
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── discussions/                 # Forum system
│   ├── models.py               # Discussion, Comment, CommentVote
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── analytics/                   # Reports & gamification
│   ├── models.py               # Badge, Certificate, PeerGroup
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── templates/                   # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── admin/
│   ├── teacher/
│   ├── student/
│   ├── courses/
│   ├── quizzes/
│   ├── discussions/
│   └── analytics/
│
├── static/                      # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
└── media/                       # User uploads
    ├── profiles/
    ├── study_materials/
    ├── assignments/
    ├── submissions/
    ├── badges/
    └── certificates/
```

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### 2. Clone and Setup

```bash
# Create project directory
mkdir educational_portal
cd educational_portal

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Create Django Project

```bash
# Create project
django-admin startproject educational_portal .

# Create apps
python manage.py startapp accounts
python manage.py startapp colleges
python manage.py startapp courses
python manage.py startapp quizzes
python manage.py startapp discussions
python manage.py startapp analytics
```

### 4. Configure Settings

Update `educational_portal/settings.py`:
- Add apps to INSTALLED_APPS
- Configure AUTH_USER_MODEL = 'accounts.User'
- Set up TEMPLATES, STATIC, and MEDIA configurations
- Configure database (SQLite for development)

### 5. Create Database

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Load Initial Data

```bash
# Create fixtures or use Django admin to add:
# 1. College instance
# 2. Departments
# 3. Users (admins, teachers, students)
# 4. Courses and sections
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## 👥 Default User Roles

### Creating Users via Django Admin

1. **College Admin**
   - Username: `admin@college.edu`
   - Role: `college_admin`
   - Has access to all management features

2. **Teacher**
   - Username: `teacher@college.edu`
   - Role: `teacher`
   - Can manage assigned courses

3. **Student**
   - Username: `student@college.edu`
   - Role: `student`
   - Can access enrolled courses

## 📝 Usage Examples

### For Admins

1. **Create Department**
   ```
   Navigate to: Colleges > Departments > Add New
   Fill in: Name, Code, HOD (optional)
   ```

2. **Register Teacher**
   ```
   Navigate to: Colleges > Teachers > Register New
   Fill in: Personal details, Employee ID, Qualification
   System creates User account automatically
   ```

3. **Register Student**
   ```
   Navigate to: Colleges > Students > Register New
   Fill in: Personal details, Roll Number, Department
   System creates User account automatically
   ```

### For Teachers

1. **Upload Study Material**
   ```
   Navigate to: My Courses > [Select Course] > Upload Material
   Choose file type: PDF, Video, Slides, or Link
   Upload file or paste link
   ```

2. **Create Assignment**
   ```
   Navigate to: My Courses > [Select Course] > Create Assignment
   Set: Title, Description, Due Date, Total Marks
   Publish when ready
   ```

3. **Mark Attendance**
   ```
   Navigate to: My Courses > [Select Course] > Mark Attendance
   Select date and mark each student's status
   ```

### For Students

1. **Submit Assignment**
   ```
   Navigate to: My Courses > [Select Course] > Assignments
   Click assignment > Upload submission
   Add optional text/comments
   ```

2. **Take Quiz**
   ```
   Navigate to: Quizzes > [Select Quiz] > Take Quiz
   Answer all questions within time limit
   Submit to see results (if enabled)
   ```

## 📈 Analytics & Reports

### SPI Calculation
- Automatically calculated based on:
  - Assignment performance (40%)
  - Quiz scores (30%)
  - Attendance percentage (20%)
  - Forum participation (10%)

### Available Reports
1. **SPI Report**: Student rankings by performance
2. **Participation Report**: Activity metrics by student
3. **At-Risk Students**: Identifies students needing attention
4. **Attendance Trends**: Visual representation over time
5. **Department Performance**: Comparative analysis

## 🎮 Gamification Features

### Badges
- **Participation Badges**: Regular activity
- **Achievement Badges**: Milestone completion
- **Excellence Badges**: Top performance
- **Consistency Badges**: Continuous engagement

### Certificates
Auto-generated for:
- Course completion
- Top performance
- Special achievements
- Participation milestones

## 🔧 Customization

### Adding New Badge Types
```python
# In Django admin or via code
Badge.objects.create(
    name="Perfect Attendance",
    badge_type="achievement",
    description="100% attendance for a semester",
    criteria={"attendance": 100, "duration": "semester"},
    points=50
)
```

### Modifying SPI Formula
Edit `Student.calculate_spi()` method in `colleges/models.py`:
```python
course_spi = (
    (0.5 * assignment_avg) +  # Changed from 0.4
    (0.3 * quiz_avg) +
    (0.1 * attendance_pct) +  # Changed from 0.2
    (0.1 * forum_score)
)
```

## 🛡️ Security Considerations

1. **Change SECRET_KEY** in production
2. **Set DEBUG = False** in production
3. **Configure ALLOWED_HOSTS** properly
4. **Use HTTPS** for production
5. **Enable CSRF protection** (enabled by default)
6. **Implement rate limiting** for API endpoints
7. **Regular security updates** for dependencies

## 🚀 Deployment

### For Production:

1. **Update settings.py**:
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   
   # Use PostgreSQL
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'eduportal_db',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

2. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

3. **Use production server** (Gunicorn/uWSGI):
   ```bash
   gunicorn educational_portal.wsgi:application
   ```

## 📞 Support & Documentation

For detailed documentation:
- Django Docs: https://docs.djangoproject.com/
- Bootstrap 5: https://getbootstrap.com/docs/5.3/
- Chart.js: https://www.chartjs.org/docs/

## 📄 License

This project is intended for educational purposes.
