from django.http import HttpResponse
from django.shortcuts import render
from .models import User
from .models import Chart
import pyrebase
import datetime

usera=User()
chart_data=Chart()

firebaseConfig={
    'apiKey': "AIzaSyA-qliY2c_fSOLRbqXwNycR0f89vGEVghU",
    'authDomain': "indian-health.firebaseapp.com",
    'projectId': "indian-health",
    'storageBucket': "indian-health.appspot.com",
    'messagingSenderId': "628925080489",
    'appId': "1:628925080489:web:44aca53e3370eac23f5ab8",
    'measurementId': "G-36KFTL185L",
    'databaseURL': "https://indian-health-default-rtdb.firebaseio.com/",
}

# Establishing connection with firebase
firebase=pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()
db=firebase.database()
storagea=firebase.storage()

def home(request):
    return render(request,'home.html')

#Login Page View
def login(request):
    if request.method=='POST':
        Username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('pswd1')
        print(email,password)
        try:
            #Check if user exists
            user=auth.sign_in_with_email_and_password(email,password)
            print(user)
            print("User Exists")
            usera.Username=Username
            usera.Email=email
            print(usera.Email,usera.Username)
            more_data=dict(db.child("Users").child(Username).get().val())
            print(more_data)
            usera.Full_Name=more_data["name"]
            usera.Gender=more_data["Gender"]
            usera.DateOfBirth=more_data["DOB"]
            usera.BloodGroup=more_data["BloodGroup"]
            usera.health_problems=more_data["list_of_Healthissues"]
            print("check1")
            if "Storage-urls" in more_data.keys():
                if "prescriptions" in more_data["Storage-urls"].keys():
                    usera.pfile_names=list(dict(more_data["Storage-urls"]["File Names"]["prescriptions"]).values())
                    usera.urls_prescriptions=dict(more_data["Storage-urls"]["prescriptions"])
                    usera.prescriptions_times=list(usera.urls_prescriptions.keys())
                    usera.prescriptions_urls=list(usera.urls_prescriptions.values())
                    print(usera.urls_prescriptions)
                   
                if "Other Files" in more_data["Storage-urls"].keys():
                    usera.ofile_names=list(dict(more_data["Storage-urls"]["File Names"]["Other Files"]).values())
                    usera.urls_Others=dict(more_data["Storage-urls"]["Other Files"])
                    usera.others_urls=list(usera.urls_Others.values())
                    usera.others_times=list(usera.urls_Others.keys())
                    print(usera.urls_Others)
            print("check2")
            #User Clusters Formation
            cluster_users=[]
            cluster_emails=[]
            HPL=list(usera.health_problems)
            #User Clusters Formation
            for i in range(0,len(HPL)):
                if Username in db.child("Clusters").child(HPL[i]).get().val():
                    print(f"{Username} already in {i} cluster")
                else:
                    db.child("Clusters").child(HPL[i]).child(Username).set(more_data["Email"])
                    print(f"{Username} added to {i} cluster")

            for i in range(0,len(HPL)):
                cluster_users.append(list(dict(db.child("Clusters").child(HPL[i]).get().val()).keys()))
                cluster_emails.append(list(dict(db.child("Clusters").child(HPL[i]).get().val()).values()))
                usera.cluster_users=list(set(cluster_users[0]))
                print(usera.cluster_users)
                usera.cluster_emails=list(set(cluster_emails[0]))
                print(usera.cluster_emails)
                return render(request,'profile.html',{'usera':usera})
            print("0012bhe")
           
        except:
            message="Invalid Credentials"
            print(message)
            return render(request,'login.html',{'msg':message})
    return render(request,'login.html')


def signin(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('psw')
        confirm_password=request.POST.get('cpsw')
        if password==confirm_password:
            try:
                print(email,password)
                user=auth.create_user_with_email_and_password(email,password)
                print(user)
            except:
                message="Unable to create user"
                print(message)
                return render(request,'signin.html',{'msg':message})

    Username = request.POST.get('uname')
    data={
        'name': request.POST.get('fname'),
        'Email': request.POST.get('email'),
        'DOB':request.POST.get('dob'),
        'Gender':request.POST.get('Gender'),
        'BloodGroup':request.POST.get('bloodgroup'),
        'list_of_Healthissues': request.POST.getlist('Healthprob[]'),
        }
    if Username not in db.child("Users").get().val().keys():
        db.child("Users").child(Username).set(data)
    else:
        message="Username already exists"
        print(message)
        return render(request,'signin.html',{'msg':message})
    return render(request,'signin.html')


def terms(request):
    return render(request, 'terms.html')

def profile(request):
    return render(request,'profile.html')

def Data(request):
    if request.method=='POST':
        #get data from the form
        Username=request.POST.get('username')
        readings=request.POST.get('readings')
        value=request.POST.get('value')
        current_time = str(datetime.datetime.now())
        #set data to the database
        db.child("Users").child(Username).child("Readings").child(readings).child(current_time[0:16]).set(value)

        #get data from the database
        Blood_Pressure_values=dict(db.child("Users").child(Username).child("Readings").child("Blood Pressure").get().val())

        Blood_Pressure_values=list(Blood_Pressure_values.values())
        if (Blood_Pressure_values != None):
            Blood_Pressure_values=[int(i) for i in Blood_Pressure_values]
            usera.Bp_vals=Blood_Pressure_values
        Blood_sugar_vals=dict(db.child("Users").child(Username).child("Readings").child("Blood Sugar").get().val())
        #User data to diplay
        if (Blood_sugar_vals!=None):
            Blood_sugar_vals=list(Blood_sugar_vals.values())
            Blood_sugar_vals=[int(i) for i in Blood_sugar_vals]
            print(Blood_sugar_vals)
            usera.Blood_Sugar=Blood_sugar_vals
            Blood_sugar_keys=dict(db.child("Users").child(Username).child("Readings").child("Blood Sugar").get().val())
            Blood_sugar_keys=list(Blood_sugar_keys.keys())
            Blood_sugar_keys=[i[5:10] for i in Blood_sugar_keys]
            print(Blood_sugar_keys)
            usera.Blood_Sugar_keys=Blood_sugar_keys

        #User data to diplay
        more_data=dict(db.child("Users").child(Username).get().val())
        usera.Full_Name=more_data["name"]
        usera.Username=Username
        usera.Email=more_data["Email"]
        usera.Gender=more_data["Gender"]
        usera.DateOfBirth=more_data["DOB"]
        usera.BloodGroup=more_data["BloodGroup"]
        usera.health_problems=more_data["list_of_Healthissues"]
        # usera.urls_prescriptions=more_data["Storage-urls"]["prescriptions"]
        # usera.urls_Others=more_data["Storage-urls"]["Others Files"]
        # usera.health_problems=more_data["list_of_Healthissues"]

        #Storage URLs and Names for prescriptions and others to be loaded to the user profile
         #get urls of files from firebase to user
        if "Storage-urls" in more_data.keys():
            if "prescriptions" in more_data["Storage-urls"].keys():
                usera.pfile_names=list(dict(more_data["Storage-urls"]["File Names"]["prescriptions"]).values())
                usera.urls_prescriptions=dict(more_data["Storage-urls"]["prescriptions"])
                usera.prescriptions_times=list(usera.urls_prescriptions.keys())
                usera.prescriptions_urls=list(usera.urls_prescriptions.values())
                print(usera.urls_prescriptions)

            if "Other Files" in more_data["Storage-urls"].keys():
                usera.ofile_names=list(dict(more_data["Storage-urls"]["File Names"]["Other Files"]).values())
                usera.urls_Others=dict(more_data["Storage-urls"]["Other Files"])
                usera.others_urls=list(usera.urls_Others.values())
                usera.others_times=list(usera.urls_Others.keys())
                print(usera.urls_Others)
                    
        #User Clusters Formation
        cluster_users=[]
        cluster_emails=[]
        HPL=list(usera.health_problems)
        #User Clusters Formation
        for i in range(0,len(HPL)):
            if Username in db.child("Clusters").child(HPL[i]).get().val():
                print(f"{Username} already in {i} cluster")
            else:
                db.child("Clusters").child(HPL[i]).child(Username).set(more_data["Email"])
                print(f"{Username} added to {i} cluster")

        for i in range(0,len(HPL)):
            cluster_users.append(list(dict(db.child("Clusters").child(HPL[i]).get().val()).keys()))
            cluster_emails.append(list(dict(db.child("Clusters").child(HPL[i]).get().val()).values()))
            usera.cluster_users=list(set(cluster_users[0]))
            print(usera.cluster_users)
            usera.cluster_emails=list(set(cluster_emails[0]))
            print(usera.cluster_emails)
    return render(request,'profile.html',{'usera':usera})

def storage(request):
    if request.method=='POST':
        #get data from form
        Username=request.POST.get('username')
        Folder=request.POST.get('folder')
        file_name=request.POST.get('file_name')
        filep=request.FILES['p_image']

        #upload file to firebase storage
        current_time = str(datetime.datetime.now())
        storagea.child("Users").child(Username).child(Folder).child(filep.name).put(filep)
        

        #get url of uploaded file
        url=storagea.child("Users").child(Username).child(Folder).child(filep.name).get_url(None)
        

        #store url and file_name in database
        db.child("Users").child(Username).child("Storage-urls").child(Folder).child(current_time[0:16]).set(url)
        db.child("Users").child(Username).child("Storage-urls").child("File Names").child(Folder).child(current_time[0:16]).set(file_name)

        #get data from firebase
        more_data=dict(db.child("Users").child(Username).get().val())
        print(more_data)
        usera.Full_Name=more_data["name"]
        usera.Username=Username
        usera.Email=more_data["Email"]
        usera.Gender=more_data["Gender"]
        usera.DateOfBirth=more_data["DOB"]
        usera.BloodGroup=more_data["BloodGroup"]
        usera.health_problems=more_data["list_of_Healthissues"]
       
        #get urls of files from firebase to user
        if "prescriptions" in more_data["Storage-urls"].keys():
            usera.pfile_names=list(dict(more_data["Storage-urls"]["File Names"]["prescriptions"]).values())
            usera.urls_prescriptions=dict(more_data["Storage-urls"]["prescriptions"])
            usera.prescriptions_times=list(usera.urls_prescriptions.keys())
            usera.prescriptions_urls=list(usera.urls_prescriptions.values())

            print(usera.urls_prescriptions)
        if "Other Files" in more_data["Storage-urls"].keys():
            usera.ofile_names=list(dict(more_data["Storage-urls"]["File Names"]["Other Files"]).values())
            usera.urls_Others=dict(more_data["Storage-urls"]["Other Files"])
            usera.others_urls=list(usera.urls_Others.values())
            usera.others_times=list(usera.urls_Others.keys())
            print(usera.urls_Others)
            
        #User Clusters Formation
        cluster_users=[]
        cluster_emails=[]
        HPL=list(usera.health_problems)
        #User Clusters Formation
        for i in range(0,len(HPL)):
            if Username in db.child("Clusters").child(HPL[i]).get().val():
                print(f"{Username} already in {i} cluster")
            else:
                db.child("Clusters").child(HPL[i]).child(Username).set(more_data["Email"])
                print(f"{Username} added to {i} cluster")

        for i in range(0,len(HPL)):
            cluster_users.append(list(dict(db.child("Clusters").child(HPL[i]).get().val()).keys()))
            cluster_emails.append(list(dict(db.child("Clusters").child(HPL[i]).get().val()).values()))
            usera.cluster_users=list(set(cluster_users[0]))
            print(usera.cluster_users)
            usera.cluster_emails=list(set(cluster_emails[0]))
            print(usera.cluster_emails)
    return render(request,'profile.html',{'usera':usera})

def refresh_clusters(request):
    #get data from firebase
    Username=request.POST.get('username')
    more_data=dict(db.child("Users").get().val())
    clusters=dict(db.child("Clusters").get().val())
    for i in more_data.keys():
        data_of_user=dict(db.child("Users").child(i).get().val())
        for k in data_of_user.keys():
            if k=='list_of_Healthissues':
                #form clusters
                for j in data_of_user[k]:
                    if j not in clusters.keys():
                        db.child("Clusters").child(j).child(i).set(data_of_user["Email"])
                        print(f"{i} added to {j} cluster")
    more_data=dict(db.child("Users").child(Username).get().val())
    usera.Full_Name=more_data["name"]
    usera.Username=Username
    usera.Email=more_data["Email"]
    usera.Gender=more_data["Gender"]
    usera.DateOfBirth=more_data["DOB"]
    usera.BloodGroup=more_data["BloodGroup"]
    usera.health_problems=more_data["list_of_Healthissues"]
    
       
    #get urls of files from firebase to user
    if "Storage-urls" in more_data.keys():
        if "prescriptions" in more_data["Storage-urls"].keys():
            usera.pfile_names=list(dict(more_data["Storage-urls"]["File Names"]["prescriptions"]).values())
            usera.urls_prescriptions=dict(more_data["Storage-urls"]["prescriptions"])
            usera.prescriptions_times=list(usera.urls_prescriptions.keys())
            usera.prescriptions_urls=list(usera.urls_prescriptions.values())

            print(usera.urls_prescriptions)
        if "Other Files" in more_data["Storage-urls"].keys():
            usera.ofile_names=list(dict(more_data["Storage-urls"]["File Names"]["Other Files"]).values())
            usera.urls_Others=dict(more_data["Storage-urls"]["Other Files"])
            usera.others_urls=list(usera.urls_Others.values())
            usera.others_times=list(usera.urls_Others.keys())
            print(usera.urls_Others)
        
        #User Clusters Formation
    cluster_users=[]
    cluster_emails=[]
    HPL=list(usera.health_problems)
        #User Clusters Formation
    for i in range(0,len(HPL)):
        if Username in db.child("Clusters").child(HPL[i]).get().val():
            print(f"{Username} already in {i} cluster")
        else:
            db.child("Clusters").child(HPL[i]).child(Username).set(more_data["Email"])
            print(f"{Username} added to {i} cluster")

    for i in range(0,len(HPL)):
        cluster_users.append(list(dict(db.child("Clusters").child(HPL[i]).get().val()).keys()))
        cluster_emails.append(list(dict(db.child("Clusters").child(HPL[i]).get().val()).values()))
        usera.cluster_users=list(set(cluster_users[0]))
        print(usera.cluster_users)
        usera.cluster_emails=list(set(cluster_emails[0]))
        print(usera.cluster_emails)
    return render(request,'profile.html',{'usera':usera})

def files(request):
    #get data from firebase
    Username=request.POST.get('username')
    more_data=dict(db.child("Users").child(Username).get().val())
    
    #get urls of files from firebase to user
    if "Storage-urls" in more_data.keys():
        if "prescriptions" in more_data["Storage-urls"].keys():
            usera.pfile_names=list(dict(more_data["Storage-urls"]["File Names"]["prescriptions"]).values())
            usera.urls_prescriptions=dict(more_data["Storage-urls"]["prescriptions"])
            usera.prescriptions_times=list(usera.urls_prescriptions.keys())
            usera.prescriptions_urls=list(usera.urls_prescriptions.values())

            print(usera.urls_prescriptions)
        if "Other Files" in more_data["Storage-urls"].keys():
            usera.ofile_names=list(dict(more_data["Storage-urls"]["File Names"]["Other Files"]).values())
            usera.urls_Others=dict(more_data["Storage-urls"]["Other Files"])
            usera.others_urls=list(usera.urls_Others.values())
            usera.others_times=list(usera.urls_Others.keys())
            print(usera.urls_Others)
        
        #User Clusters Formation
    return render(request,'storage.html',{'usera':usera})

def visualize(request):
    #get data from firebase
    Username=request.POST.get('username')
    print(Username)
    more_data=dict(db.child("Users").child(Username).child("Readings").get().val())
    if "Blood Pressure" in more_data.keys():
        bloodPressure=more_data["Blood Pressure"]
        bloodPressure_dates=list(bloodPressure.keys())
        bloodPressure_values=list(bloodPressure.values())
        chart_data.dates_bp=[x[5:] for x in bloodPressure_dates]
        chart_data.values_bp=bloodPressure_values
        print(bloodPressure_dates)
        print(bloodPressure_values)
    else:
        chart_data.dates_bp=[]
        chart_data.values_bp=[]
    if "Heart Rate" in more_data.keys():
        heartRate=more_data["Heart Rate"]
        heartRate_dates=list(heartRate.keys())
        heartRate_values=list(heartRate.values())
        chart_data.dates_hr=[x[5:] for x in heartRate_dates]
        chart_data.values_hr=heartRate_values
        print(heartRate_dates)
        print(heartRate_values)
    else:
        chart_data.dates_hr=[]
        chart_data.values_hr=[]
    if "Blood Sugar" in more_data.keys():
        bloodSugar=more_data["Blood Sugar"]
        bloodSugar_dates=list(bloodSugar.keys())
        bloodSugar_values=list(bloodSugar.values())
        chart_data.dates_bs=[x[5:] for x in bloodSugar_dates]
        chart_data.values_bs=bloodSugar_values
        print(bloodSugar_dates)
        print(bloodSugar_values)
    else:
        chart_data.dates_bs=[]
        chart_data.values_bs=[]
    if "Weight" in more_data.keys():
        weight=more_data["Weight"]
        weight_dates=list(weight.keys())
        weight_values=list(weight.values())
        chart_data.dates_weight=[x[5:] for x in weight_dates]
        chart_data.values_weight=weight_values
        print(weight_dates)
        print(weight_values)
    else:
        chart_data.dates_weight=[]
        chart_data.values_weight=[]
    return render(request,'visualize.html',{'chart_data':chart_data})