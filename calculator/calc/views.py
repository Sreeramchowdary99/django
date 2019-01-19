from django.shortcuts import render

# Create your views here.
def calc(requests):
    field1=requests.GET['field1']
    field2=requests.GET['field2']
    opeartion=requests.GET['optradio']
    result=0
    if opeartion == '+':
        result=int(field1)+int(field2)
    elif opration == '-':
        result=int(field1)-int(field2)
    elif opration == '*':
        result=int(field1)*int(field2)
    else :
        result=int(field1)/int(field2) 
    return render(requests,'calc/calc.html',{'result':result})
def home(requests):
    return render(requests,'calc/home.html')
