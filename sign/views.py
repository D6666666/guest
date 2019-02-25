from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event,Guest
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger


# Create your views here.

# def index(request):
#     return HttpResponse("Hello World!")
def index(request):
    return render(request,"index.html")

#登陆动作
def login_action(request):
    if request.method == "POST":
        username = request.POST.get('username','')
        password = request.POST.get('password', '')
        #if username == 'admin' and password == 'admin123':
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            request.session['user'] = username
            response = HttpResponseRedirect('/event_manage/')
            #return HttpResponse('Login Success!')
            #return HttpResponseRedirect('/event_manage/')
            #response.set_cookie('user',username,3600)
            return response
        else:
            return render(request,'index.html',{'error':"用户名或者密码错误！"})

#发布会管理
@login_required
def event_manage(request):
    #username = request.COOKIES.get('user','')
    event_list = Event.objects.all()
    username = request.session.get('user','')
    return render(request,'event_manage.html',{"user":username,'events':event_list})

#发布会名称搜索
@login_required
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get("name",'')
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request,"event_manage.html",{"user":username,'events':event_list})

#嘉宾管理
@login_required
def guest_manage(request):
    #username = request.COOKIES.get('user','')
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()
    paginator = Paginator(guest_list,2)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1) #如果page不是整数，取第一页数据
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)  #如果page不在范围内，取最后一页
    return render(request,'guest_manage.html',{"user":username,'guests':contacts})

#嘉宾名称搜索
@login_required
def search_guest(request):
    username = request.session.get('user', '')
    search_guest = request.GET.get("name",'')
    guest_list = Guest.objects.filter(phone__contains=search_guest)
    paginator = Paginator(guest_list, 2)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)  # 如果page不是整数，取第一页数据
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)  # 如果page不在范围内，取最后一页
    return render(request,"guest_manage.html",{"user":username,'guests':contacts})

#签到页面
@login_required
def sign_index(request,eid):
    event = get_object_or_404(Event,id=eid)
    num = len(Guest.objects.filter(event_id=eid,sign='1'))
    return render(request,"sign_index.html",{"event":event,'num':num})

#签到动作
@login_required
def sign_index_action(request,eid):
    event = get_object_or_404(Event, id=eid)
    phone = request.POST.get('phone','')
    num = len(Guest.objects.filter(event_id=eid, sign='1'))
    print(phone)
    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request,"sign_index.html",{'event':event,'hint':"phone error.",'num':num})
    result = Guest.objects.filter(phone=phone,event_id=eid)
    if not result:
        return render(request,"sign_index.html",{'event':event,'hint':"event id or phone error.",'num':num})
    result = Guest.objects.get(phone=phone, event_id=eid)
    if result.sign:
        return render(request, "sign_index.html", {'event': event, 'hint': "user has sign in.",'num':num})
    else:
        Guest.objects.filter(phone=phone, event_id=eid).update(sign='1')
        return render(request, "sign_index.html", {'event': event, 'hint': "sign in success.","guest":result
                                                   ,'num':num})

#退出登陆
@login_required
def logout(request):
    auth.logout(request)
    respones = HttpResponseRedirect('/index/')
    return respones