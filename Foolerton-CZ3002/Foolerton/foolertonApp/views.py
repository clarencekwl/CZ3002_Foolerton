from xml.etree.ElementTree import Comment
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User, Task
from .models import *
# Create your views here.


def test(request):

    return render(request, 'base.html')


def createUser(request):

    if request.method == "GET":
        return render(request, 'register_page.html')

    if request.method == "POST":
        if request.POST['password'] != request.POST['repassword']:
            return render(request, 'register_page.html', {'message': 'password do not match'})

        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        userType = 'careTaker'
        use = User.objects.create_user(
            email, name, password)
        use.user_type = userType
        use.save()
        # if(userType == 'careTaker'):
        #     nric = request.POST['nric']
        #     care = CaretakerToPatient.objects.create(
        #         Caretaker=use, Patient=Patient.objects.get(NRIC=nric))
        #     care.save()
        content = {'Success': "created for " + use.name}
        return render(request, 'register_page.html', content)


def createtasks(request, name):
    if request.method == "GET":
        user = request.user
        if(user.user_type == 'doctor'):
            patients = DoctorToPatient.objects.filter(Doctor=user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            tasklist = Task.objects.all().filter(
                Patient__name=name).order_by('time')
            comment = []
            for i in tasklist:
                comments = i.comment_task.all()
                comment.append({"tasked": i, "comment": comments})
            context = {
                'comments': comment,
                # 'tasklist': tasklist,
                'people': ppl,
                'current': name,
                'name': request.user.name
            }
            print(comment)
            return render(request, 'tasks_page_main.html', context)
        if(user.user_type == 'careTaker'):
            patients = CaretakerToPatient.objects.filter(Caretaker=user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            tasklist = Task.objects.all().filter(
                Patient__name=name).order_by('time')
            comment = []
            for i in tasklist:
                comments = i.comment_task.all()
                comment.append({"tasked": i, "comment": comments})
            context = {
                'comments': comment,
                # 'tasklist': tasklist,
                'people': ppl,
                'current': name,
                'name': request.user.name
            }
            return render(request, 'tasks_page_main_care.html', context)


def createdtasks(request):
    if request.method == "POST":
        if request.POST.get("form_type") == 'addtask':

            name = request.POST.get('person')
            Patiented = Patient.objects.filter(
                name=name).first()  # testing
            date = request.POST.get('datecomplete')
            time = request.POST.get('timecomplete')
            details = request.POST.get('taskdesc')
            editBy = 'test'
            Patient_id = 1
            newTask = Task(date=date, Patient=Patiented,
                           time=time, details=details, editBy=editBy)
            newTask.save()
            whr = '/createtasks/'+name
            return redirect(whr)
    # just load this first if it doesnt work
    return render(request, 'loginpg.html')


def createcomments(request):
    if request.method == "POST":
        Tasked = Task.objects.filter(pk=request.POST.get('task')).first()
        comment = request.POST.get('commet')
        com = Comments.objects.create(
            task=Tasked, comment=comment, editBy=request.user.name, editDate=timezone.now())
        com.save()
        name = request.POST.get('name')
        whr = '/createtasks/'+name
        return redirect(whr)


def updatetasks(request):
    if request.method == "POST":
        if request.POST.get("form_type") == 'updatetask':

            name = request.POST.get('name')
            Patiented = Patient.objects.filter(
                name=name).first()  # testing
            date = request.POST.get('datecomplete')
            time = request.POST.get('timecomplete')
            details = request.POST.get('taskdesc')
            editBy = request.user.name
            # Patient_id = 1
            newTask = Task.objects.filter(pk=request.POST.get('task')).first()
            newTask.date = date
            newTask.time = time
            newTask.details = details
            newTask.editBy = editBy
            newTask.save()
            whr = '/createtasks/'+name
            return redirect(whr)
    # just load this first if it doesnt work
    return render(request, 'loginpg.html')


def deleteTask(request, id):
    task = Task.objects.get(id=id)
    context = {'task': task}

    if request.method == 'POST':
        task.delete()
        return redirect('/createtasks')
    return render(request, 'delete_task.html', context)


def login_user(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 'doctor':
                patients = DoctorToPatient.objects.filter(Doctor=user).first()
                # tasklist = Task.objects.all().filter(Patient_id=1)  # testing so Patient_id = 1

                whr = '/createtasks/'+patients.Patient.name
                return redirect(whr)
            if user.user_type == 'careTaker':
                patients = CaretakerToPatient.objects.filter(
                    Caretaker=user).first()
                # tasklist = Task.objects.all().filter(Patient_id=1)  # testing so Patient_id = 1
                if patients == None:
                    patients = "-"
                else:
                    patients = patients.Patient.name
                whr = '/createtasks/'+patients
                return redirect(whr)
        else:
            message = "unsuccessful login! Please enter the right email and password!"
            return render(request, 'login_page.html', {'message': message})
    if request.method == "GET":
        return render(request, 'login_page.html')


def view_tasks(request):
    if request.method == "GET":
        query_tasks = Task.objects.filter(
            Patient=request.GET['patient_id'],
            date=request.GET['date']
        ).order_by('number')
        if query_tasks is not None:
            tasks_comments_dict = {}
            for task in query_tasks:
                # cant seem to fetch comments due to conversion error?
                query_comment = Comments.objects.filter(task_id=task.id)
                if query_comment is not None:
                    comments_dict = {
                        comment.id: comment for comment in query_comment}
                    tasks_comments_dict[task.number] = (
                        task, comments_dict)
                else:
                    tasks_comments_dict[task.number] = (task, None)
            print(tasks_comments_dict)
            return render(request, 'testpage.html', {'task_query': tasks_comments_dict})
    return render(request, 'testpage.html', {'task_query': None})


def mark_task_as_completed(request):
    if request.method == "POST":
        task = Task.objects.filter(id=request.POST['task_id'])
        print(task)
        task.completedFlag = True
        try:
            task.save()
        except Task.DoesNotExist:
            print("Task does not exist")
            return
        except Exception:
            print("error in saving task")
            print(Exception)
            return
        print("Task marked as completed")
        return render(request, 'testpage.html')
    elif request.method == "GET":
        return render(request, 'testpage.html')


def upload_medical(request):
    if request.method == "POST":
        patient_id = request.POST['patient_id']
        date = request.POST['date']
        blood_pressure = request.POST['blood_pressure']
        height = request.POST['height']
        weight = request.POST['weight']

        patient_medical = MedicalDetails.objects.get(Patient=patient_id)

        patient_medical.bloodPressure = blood_pressure
        patient_medical.height = height
        patient_medical.weight = weight
        patient_medical.save()

        return render(request, 'testpage.html')

    elif request.method == "GET":
        return render(request, 'testpage.html')


def healthinfo(request, name):
    if request.method == "GET":
        if(request.user.user_type == 'doctor'):
            patients = DoctorToPatient.objects.filter(Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            patient = Patient.objects.get(name=name)
            details = MedicalDetails.objects.get(Patient=patient)

            return render(request, 'health_info.html', {'pat': patient, 'det': details, 'current': name, 'people': ppl, 'name': request.user.name})
        if(request.user.user_type == 'careTaker'):
            patients = CaretakerToPatient.objects.filter(
                Caretaker=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            patient = Patient.objects.get(name=name)
            details = MedicalDetails.objects.get(Patient=patient)

            return render(request, 'health_info.html', {'pat': patient, 'det': details, 'current': name, 'people': ppl, 'name': request.user.name})


def docacc(request):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        return render(request, 'doc_account_main.html', {'name': request.user.name, "people": ppl, "current": ppl[0].name, "email": request.user.email})
    if request.method == "POST":
        whr = '/'+request.POST.get('options')
        return redirect(whr)


def logoutacc(request):

    logout(request)
    whr = 'http://127.0.0.1:8000/login'
    return redirect(whr)


def manage(request):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        return render(request, 'manage_patient_profiles.html', {"name": request.user.name, "people": ppl})
    if request.method == "POST":
        user = request.user
        act = request.POST.get('action')
        person = request.POST.get('person')
        if(act == 'addpat'):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            return render(request, 'create_patient_profile.html', {"people": ppl, "name": request.user.name, "current": ppl[0].name})
        if(act == 'removepat'):

            pat = Patient.objects.filter(name=person).first()
            pat.delete()
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            return render(request, 'manage_patient_profiles.html', {"message": "successfully deleted "+person, "people": ppl, "current": ppl[0].name, "name": request.user.name})
        if(act == 'addcare'):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            whr = 'http://127.0.0.1:8000/addcare/'+person
            return redirect(whr)
            return render(request, 'add_caretaker.html', {"pat": person, "people": ppl, "name": request.user.name, "current": ppl[0].name})
        if(act == 'removecare'):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            whr = 'http://127.0.0.1:8000/removecare/'+person
            return redirect(whr)
            return render(request, 'create_patient_profile.html', {"pat": person, "people": ppl, "name": request.user.name})


def removecare(request, pat):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        care = CaretakerToPatient.objects.filter(Patient__name=pat)
        caretakers = []
        for i in care:
            caretakers.append(i.Caretaker)

        return render(request, 'remove_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].name, "patient": pat, "caretakers": caretakers})


def addcare(request, pat):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)

        return render(request, 'add_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].name, "patient": pat})
    if request.method == "POST":
        email = request.POST.get('email')
        care = User.objects.filter(email=email).first()
        patient = Patient.objects.filter(name=pat).first()
        connect = CaretakerToPatient.objects.create(
            Caretaker=care, Patient=patient)
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        return render(request, 'add_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].name, "message": "successfully added "+care.name+" to "+pat, "patient": pat})


def createpat(request):
    if request.method == "POST":
        name = request.POST.get('name')
        nric = request.POST.get('nric')
        pat = Patient.objects.create(NRIC=nric, name=name)
        connect = DoctorToPatient.objects.create(
            Patient=pat, Doctor=request.user)
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        return render(request, 'create_patient_profile.html', {"name": request.user.name, "current": ppl[0].name, "people": ppl, "message": "successfully created "+name})


def update(request):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        return render(request, 'doc_account_update.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": ppl[0].name})
    if request.method == 'POST':
        user = request.user
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        print(request.POST.get('email'), 'try')
        user.email = request.POST.get('email')
        user.name = request.POST.get('name')
        user.save()
        return render(request, 'doc_account_update.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": ppl[0].name})


def change(request):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": ppl[0].name})
    if request.method == 'POST':
        user = request.user
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        if(user.password != request.POST.get('old_password')):
            return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, 'wrongpassword': "please enter the right password", "current": ppl[0].name})
        user.password = request.POST.get('new_password')
        user.save()
        return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": ppl[0].name})
