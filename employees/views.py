from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employee, Department
from accounts.models import User
from accounts.decorators import manager_required
from audit.utils import log_action


@login_required
def employee_list(request):
    employees = Employee.objects.select_related('user', 'department').order_by('-created_at')

    status = request.GET.get('status')
    if status:
        employees = employees.filter(status=status)

    search = request.GET.get('search', '')
    if search:
        employees = employees.filter(
            user__first_name__icontains=search
        ) | employees.filter(
            user__last_name__icontains=search
        ) | employees.filter(
            user__email__icontains=search
        )

    context = {
        'employees':    employees,
        'total':        Employee.objects.count(),
        'active':       Employee.objects.filter(status='active').count(),
        'on_leave':     Employee.objects.filter(status='on_leave').count(),
        'inactive':     Employee.objects.filter(status='inactive').count(),
        'departments':  Department.objects.all(),
        'selected_status': status or '',
        'search': search,
    }
    return render(request, 'employees/employee_list.html', context)


@manager_required
@login_required
def employee_create(request):
    if request.method == 'POST':
        # User fields
        first_name  = request.POST.get('first_name', '')
        last_name   = request.POST.get('last_name', '')
        email       = request.POST.get('email', '')
        job_title   = request.POST.get('job_title', '')
        phone       = request.POST.get('phone', '')

        # Employee fields
        employee_id     = request.POST.get('employee_id', '')
        department_id   = request.POST.get('department') or None
        status          = request.POST.get('status', 'active')
        date_of_joining = request.POST.get('date_of_joining') or None
        salary          = request.POST.get('salary') or None

        if not email:
            messages.error(request, 'Email is required.')
            return redirect('employee_create')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return redirect('employee_create')

        # Create user
        username = email.split('@')[0]
        base     = username
        counter  = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            phone=phone,
            role=request.POST.get('role', 'employee'),
            password='NexaOps@2026',
        )

        employee = Employee.objects.create(
            user=user,
            employee_id=employee_id or f'EMP{User.objects.count():04d}',
            department_id=department_id,
            status=status,
            date_of_joining=date_of_joining,
            salary=salary,
        )
        log_action(request, 'create', 'Employee', user.get_full_name(), employee.pk)

        messages.success(request, f'Employee {first_name} {last_name} added successfully! Default password: NexaOps@2026')
        return redirect('employee_list')

    context = {
        'departments': Department.objects.all(),
        'emp_count':   Employee.objects.count() + 1,
    }
    return render(request, 'employees/employee_form.html', context)


@manager_required
@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    user     = employee.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.job_title = request.POST.get('job_title', '')
        user.phone = request.POST.get('phone', '')
        user.role = request.POST.get('role', user.role)
        user.save()

        employee.employee_id = request.POST.get('employee_id', employee.employee_id)
        employee.department_id = request.POST.get('department') or None
        employee.status = request.POST.get('status', 'active')
        employee.date_of_joining = request.POST.get('date_of_joining') or None
        employee.salary = request.POST.get('salary') or None
        employee.save()
        log_action(request, 'update', 'Employee', user.get_full_name(), employee.pk)

        messages.success(request, f'Employee {user.get_full_name()} updated!')
        return redirect('employee_list')

    context = {
        'employee':    employee,
        'departments': Department.objects.all(),
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    context  = {
        'employee': employee,
        'tasks':    employee.user.assigned_tasks.order_by('-created_at')[:5],
    }
    return render(request, 'employees/employee_detail.html', context)


@manager_required
@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = employee.user.get_full_name()
        log_action(request, 'delete', 'Employee', name, pk)
        employee.user.delete()
        messages.success(request, f'Employee {name} removed.')
    return redirect('employee_list')


# ---------- Departments ----------

@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'employees/department_list.html', {'departments': departments})


@manager_required
@login_required
def department_create(request):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        description = request.POST.get('description', '')
        if not name:
            messages.error(request, 'Department name is required.')
            return redirect('department_create')
        if Department.objects.filter(name=name).exists():
            messages.error(request, 'Department already exists.')
            return redirect('department_create')
        Department.objects.create(name=name, description=description)
        messages.success(request, f'Department "{name}" created!')
        return redirect('department_list')
    return render(request, 'employees/department_form.html')


@manager_required
@login_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, 'Department deleted.')
    return redirect('department_list')