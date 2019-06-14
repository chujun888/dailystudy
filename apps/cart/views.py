from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import JsonResponse
from django_redis import get_redis_connection

from goods.models import GoodsSKU
#from django_redis import get_redis_connection
from utilsa.mixin import LoginRequiredMixin

# Create your views here.
# 添加商品到购物车:
# 1）请求方式，采用ajax post
# 如果涉及到数据的修改(新增，更新，删除), 采用post
# 如果只涉及到数据的获取，采用get
# 2) 传递参数: 商品id(sku_id) 商品数量(count)
class CartAddView(View):
	'''购物车记录添加'''
	def post(self,request):
		user = request.user
		sku_id = request.POST.get("sku_id")
		count  = request.POST.get("count")
		if not user.is_authenticated:
			return JsonResponse({"res":5,"errmsg":"用户未登录"})
		if not all([sku_id,count]):
			return JsonResponse({"res":0,"errmsg":"数据不完整"})
		try:
			count = int(count)
		except Exception as e:
			return JsonResponse({"res":1,"errmsg":"数据不完整"})
		#校验商品是否存在
		try:
			sku = GoodsSKU.objects.get(id = sku_id)
		except GoodsSKU.DoesNotExist:
			return JsonResponse({"res":2,"errmsg":"商品不存在"})
		#添加购物车记录
		conn = get_redis_connection('default')
		cart_key = 'cart_%d'%user.id
		cart_count = conn.hget(cart_key,sku_id)
		if cart_count:
			count += int(cart_count)
		print(count)
		print(sku_id)
		conn.hset(cart_key,sku_id,count)
		return JsonResponse({"res":3,"errmsg":"商品添加成功"})

	def get(self,request):
		pass

# /cart/
class CartInfoView(View):
    '''购物车页面显示'''
    def get(self, request):
        '''显示'''
        # 获取登录的用户
        user = request.user
        # 获取用户购物车中商品的信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # {'商品id':商品数量, ...}
        cart_dict = conn.hgetall(cart_key)

        skus = []
        # 保存用户购物车中商品的总数目和总价格
        total_count = 0
        total_price = 0
        # 遍历获取商品的信息
        for sku_id, count in cart_dict.items():
            # 根据商品的id获取商品的信息
            sku    = GoodsSKU.objects.get(id=sku_id)
            print(count)
            print(cart_dict)
            print(cart_dict.items())
            # 计算商品的小计
            amount     = sku.price*int(count)
            # 动态给sku对象增加一个属性amount, 保存商品的小计
            sku.amount = amount
            # 动态给sku对象增加一个属性count, 保存购物车中对应商品的数量
            sku.count  = int(count)
            # 添加
            skus.append(sku)
            # 累加计算商品的总数目和总价格
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = {'total_count':total_count,
                   'total_price':total_price,
                   'skus':skus}

        # 使用模板
        return render(request, 'cart.html', context)
class CartDeleteView(View):
	def get(self,request):
		pass
	def post(self,request):
		user = request.user
		sku_id = request.POST.get("sku_id")
		if not user.is_authenticated:
			return JsonResponse({"res":5,"errmsg":"用户未登录"})
		if not sku_id:
			return JsonResponse({"res":1,"errmsg":"无效的商品ID"})
		try:
			sku = GoodsSKU.objects.get(id=sku_id)
		except:
			return JsonResponse({"res":1,"errmsg":"商品不存在"})
		#业务处理 删除购物车处理
		conn  = get_redis_connection('default')
		cart_key = 'cart_%d' % user.id 
		conn.hdel(cart_key,sku_id)
		return JsonResponse({"res":3,"errmsg":"删除成功"})

		

class CartUpdateView(View):
	def get(self,request):
		pass

	def post(self,request):
		user = request.user
		sku_id = request.POST.get("sku_id")
		count  = request.POST.get("count")
		if not user.is_authenticated:
			return JsonResponse({"res":5,"errmsg":"用户未登录"})
		if not all([sku_id,count]):
			return JsonResponse({"res":0,"errmsg":"数据不完整"})
		try:
			count = int(count)
		except Exception as e:
			return JsonResponse({"res":1,"errmsg":"数据不完整"})
		#校验商品是否存在
		try:
			sku = GoodsSKU.objects.get(id = sku_id)
		except GoodsSKU.DoesNotExist:
			return JsonResponse({"res":2,"errmsg":"商品不存在"})
		conn = get_redis_connection('default')
		cart_key = 'cart_%d'%user.id
		conn.hset(cart_key,sku_id,count)



