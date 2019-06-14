from django.shortcuts import render,redirect
from django.urls import reverse
from user.models import User,Address
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_email
from django.contrib.auth import authenticate, login
from utilsa.mixin import LoginRequiredMixin
from redis import StrictRedis
from goods.models import GoodsSKU 
# django.config import settings
import re
class RegisterView(View):
	def get(self,request):
		return render(request,'register.html')
	def post(self,request):
		user_name = request.POST.get("user_name")
		email     = request.POST.get("email")
		pwd       = request.POST.get("pwd")
		if not all([user_name,email,pwd]):
			return render(request,'register.html',{'errmsg':'信息不完整'})

	    #校验邮箱
		if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
			return render(request,'register.html',{'errmsg':'邮箱格式不正确'})
	    #校验用户名是否重复
		try:
			user = User.objects.get(username=user_name)
		except User.DoesNotExist: 
			user = None
		if user:
			return render(request,'register.html',{'errmsg':'用户名已存在'})

		user = User.objects.create_user(user_name,email,pwd)
		user.is_active = 1
		user.save()
		# serializer = Serializer(settings.SECRET_KEY, 3600)
		# info = {'confirm':user.id}
		# token = serializer.dumps(info)
		# #发邮件
		# send_register_email.delay(email,user_name,token)
		return redirect(reverse("goods:index"))

class ActiveView(View):
	def get(self,request,token):
		serializer = Serializer(settings.SECRET_KEY, 3600)
		try:
			info = serializer.loads(token)
			user_id = info['confirm']
			user = User.objects.get(id=user_id)
			user.is_active = 1
			user.save()
			# 跳转到登录页面
			redirect(reverse("user:login"))
		except SignatureExpired as e:
			#激活链接已过期
			return HttpResponse("激活链接已过期")

class LoginView(View):
	def get(self,request):
		if 'username' in request.COOKIES:
			username = request.COOKIES.get('username')
			checked = 'checked'
		else:
			username = ''
			checked = ''

		return render(request,"login.html",{'username':username,'checked':checked})

	def post(self,request):
		#接收数据
		username = request.POST.get("username")
		pwd = request.POST.get("pwd")

		#校验数据
		if not all([username,pwd]):
			return render(request,"login.html")
		#业务处理
        # 业务处理:登录校验
		user = authenticate(username=username, password=pwd)
		if user is not None:
            # 用户名密码正确
			if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
				login(request,user)
				url = request.GET.get("next",reverse("goods:index"))
				response = redirect(url)
                # 用户未激活
				#判断是否记住用户名
				remember = request.POST.get("remember")
				if remember == "on":
					reponse.set_cookie("username",username,max_age=7*24*3600)
				else:
					response.delete_cookie("username")
				return response
			else:
                # 用户未激活
				return render(request, 'login.html', {'errmsg':'账户未激活'})
		else:
            # 用户名或密码错误
			return render(request, 'login.html', {'errmsg':'用户名或密码错误'})
		#返回应答

#用户中心页面
class UserInfoView(LoginRequiredMixin,View):
	def get(self,request):
		#获取用户个人信息
		conn = StrictRedis(host='localhost', port=6379, db=0)
		user  = request.user
		history_key = 'history_%d'%user.id
		sku_ids = conn.lrange(history_key,0,4)
		#从数据库查找商品浏览的具体信息
		goods_li = []
		for i in sku_ids:
			goods_li.append(GoodsSKU.objects.get(id=i))
		page = 'user'

		context = {'page':page,'goods_li':goods_li}	
		#获取用户历史浏览记录
		return render(request,'user_center_info.html',context)
	def post(self,request):
		page = 'user'
		return render(request,'user_center_info.html',{'page':page})

#用户订单页面
class UserOrderView(LoginRequiredMixin,View):
	def get(self,request):
		page = 'order'
		return render(request,'user_center_order.html',{'page':page})
	def post(self,request):
		page = 'order'
		return render(request,'user_center_order.html',{'page':page})

class AddressView(LoginRequiredMixin,View):
	def get(self,request):
		page = 'address'
		user = request.user
		address = Address.objects.get_default_address(user)
		return render(request,'user_center_site.html',{'page':page,'address':address})
	def post(self,request):
		page = 'address'
		receiver = request.POST.get("receiver")
		addr     = request.POST.get("addr")
		zip_code = request.POST.get("zip_code")
		phone 	 = request.POST.get("phone")
		if not all([receiver,addr,phone]):
			return render(request,'user_center_site.html',{'page':page,'errmsg':'数据不完整'})
		if not re.match(r'^1[3|4|5|7|8][0-9]{9}$',phone):
			return render(request,'user_center_site.html',{'page':page,'errmsg':"手机格式不正确"})
		user = request.user
		address = Address.objects.get_default_address(user)
		if address:
			is_default = False
		else:
			is_default = True
		#添加地址
		Address.objects.create(user=user,addr=addr,is_default=is_default,phone=phone)
		return redirect(reverse("user:address"))
		#添加时存在默认地址，则非默认，否则默认
		#return render(request,'user_center_site.html',{'page':page})

#退出登录
class LogoutView(View):
	def get(self,request):
		logout(request)
		#跳转到首页
		return redirect(reverse("goods:index"))

