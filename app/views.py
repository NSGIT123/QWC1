import pickle
import pandas as pd
from sklearn import *
import serial
from django.shortcuts import render, redirect
from django.contrib.auth import 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from app import forms
from app.models import communities



def homepage(request):
    return render(request, 'index.html')

@login_required()
def monitor(request):
    try:
        connectionerror = 'No Connection Errors'
        scaler = pickle.load(open('scaler.pkl', 'rb'))
        pca = pickle.load(open('pca.pkl', 'rb'))
        model = pickle.load(open('model.pkl', 'rb'))
        arduino = serial.Serial('COM3', 9600, timeout=1)
        sensorreadings = arduino.readline().decode('utf-8')
        sensormetrics = sensorreadings.split(',')
        metrics = pd.DataFrame(
            {"ph": [sensormetrics[0]], "Solids": [sensormetrics[4]], "Conductivity": [sensormetrics[5]],
             "Turbidity": [sensormetrics[1]]})
        scaled_data = scaler.transform(metrics)
        pca_data = pca.transform(scaled_data)
        prediction = model.predict(pca_data)
        output = prediction[0]
        if output == 0:
            quickoutput = 'NOT SAFE'
            output = 'Your water is not safe. Please take the Contaminant Quiz to learn more about your water and next steps.'
            context = {'pH': sensormetrics[0],
                       'turbidity': sensormetrics[1],
                       'ctemperature': sensormetrics[2],
                       'ftemperature': sensormetrics[3],
                       'tds': sensormetrics[4],
                       'conductivity': sensormetrics[5],
                       'salinity': sensormetrics[6],
                       'error': connectionerror,
                       'quickoutput': quickoutput,
                       'output': output}
        else:
            quickoutput = 'SAFE'
            output = 'Your water is safe!'
            context = {'pH': sensormetrics[0],
                       'turbidity': sensormetrics[1],
                       'ctemperature': sensormetrics[2],
                       'ftemperature': sensormetrics[3],
                       'tds': sensormetrics[4],
                       'conductivity': sensormetrics[5],
                       'salinity': sensormetrics[6],
                       'error': connectionerror,
                       'quickoutput': quickoutput,
                       'output': output}
    except:
        connectionerror = 'Please Check the Connection and Port'
        context = {
            'error': connectionerror
        }
    return render(request, 'monitoryourwater.html', context)

@login_required()
def test(request):
    onehotencoder = pickle.load(open('onehotencoder.pkl', 'rb'))
    contaminanttestmodel = pickle.load(open('contaminanttestmodel.pkl', 'rb'))
    if request.method == 'POST':
        if request.POST.get('step') == '2':
            createcomm = forms.Createcommunity()
            comm = communities.objects.filter(user=request.user)
            if request.method == 'POST':
                if request.POST.get('step') == '1':
                    createcomm = forms.Createcommunity(request.POST)
                    if createcomm.is_valid():
                        create_comm = createcomm.save(commit=False)
                        create_comm.user = request.user
                        create_comm.save()
            odor = request.POST.get('odor')
            color = request.POST.get('color')
            taste = request.POST.get('taste')
            input = {'Odor': odor, 'Color': color, 'Taste': taste}
            df = pd.read_excel(r'Contaminant Data.xlsx')
            df = df.drop('Extras for later', axis=1)
            df = df.append(input, ignore_index=True)
            X = df.drop('Contaminants', axis=1)
            X = onehotencoder.transform(X)
            predictions = contaminanttestmodel.predict(X)
            if predictions[34] == 'Fluoride':
                predictions[34] = 'Fluoride, Nitrates/Nitrites, or Radioactive Elements'
            elif predictions[34] == 'Nitrates/Nitrites':
                predictions[34] = 'Fluoride, Nitrates/Nitrites, or Radioactive Elements'
            elif predictions[34] == 'Radioactive Elements':
                predictions[34] = 'Fluoride, Nitrates/Nitrites, or Radioactive Elements'
            else:
                predictions[34] = predictions[34]
            context = {
                'predictions': predictions[34],
                'createcomm': createcomm,
                'comm': comm,
            }
            return render(request, 'takecontaminantquiz.html', context)
    createcomm = forms.Createcommunity()
    comm = communities.objects.filter(user=request.user)
    if request.method == 'POST':
        if request.POST.get('step') == '1':
            createcomm = forms.Createcommunity(request.POST)
            if createcomm.is_valid():
                create_comm = createcomm.save(commit=False)
                create_comm.user = request.user
                create_comm.save()
    return render(request, 'takecontaminantquiz.html', {'createcomm':createcomm, 'comm':comm,})

@login_required()
def viewcommunity(request, name_of_community):
    if request.method == 'POST':
        prediction = request.POST.get("pred")
        comm = communities.objects.get(community=name_of_community)
        comm.predictions = str(comm.predictions) + ',' + str(prediction)
        comm.save()
    predcomm = communities.objects.get(community=name_of_community)
    if predcomm.predictions is not None:
        preds = predcomm.predictions.split(',')
        preds.remove('None')
        unique = []
        count = []
        for preds in preds:
            if preds not in unique:
                unique.append(preds)
        for uniques in unique:
            num = predcomm.predictions.split(',').count(uniques)
            count.append(num)
        preddict = dict(zip(unique, count))
        return render(request, 'communitypred.html', {'name_of_community': name_of_community, 'preddict': preddict, })
    return render(request, 'communitypred.html', {'name_of_community':name_of_community,})

@login_required()
def information(request):
    return render(request,'contaminantsinformation.html')

@login_required()
def usersurvey(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'potability':
            ph = request.POST.get('ph')
            turbidity = request.POST.get('turbidity')
            ctemperature = request.POST.get('ctemperature')
            ftemperature = request.POST.get('ftemperature')
            tds = request.POST.get('tdsresult')
            conductivity = request.POST.get('conductivity')
            salinity = request.POST.get('salinity')
            potability = request.POST.get('potability')
            input = {'pH': ph, 'turbidity': turbidity, 'ctemperature': ctemperature, 'ftemperature': ftemperature, 'tds' : tds, 'conductivity': conductivity, 'salinity': salinity, 'potability': potability}
            df = pd.read_csv(r'potabilityusersurvey.csv')
            df = df.append(input, ignore_index=True)
            df.to_csv(r"potabilityusersurvey.csv", index=False)
        if request.POST.get('action') == 'contaminant':
            odor = request.POST.get('odor')
            color = request.POST.get('color')
            taste = request.POST.get('taste')
            contaminant = request.POST.get('contaminant')
            input = {'Odor': odor, 'Color': color, 'Taste': taste, 'Contaminant': contaminant}
            df = pd.read_csv(r'contaminantusersurvey.csv')
            df = df.append(input, ignore_index=True)
            df.to_csv("contaminantusersurvey.csv", index=False)
    return render(request,'usersurvey.html')

@login_required()
def profile(request):
    user_form = forms.BasicUserForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        if request.POST.get('action') == 'update_profile':
            user_form = forms.BasicUserForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('/profile/')
        elif request.POST.get('action') == 'update_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request,user)
                messages.success(request, 'Your profile has been updated.')
                return redirect('/profile/')
    return render(request, 'profile.html', {
        "user_form": user_form,
        "password_form": password_form,
    })


def sign_up(request):
    form = forms.SignUpForm()
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = form.save(commit=False)
            user.username = email
            user.save()
            login(request, user)
            return redirect('/log-in/')
    return render(request, 'sign_up.html', {
        'form': form
    })

