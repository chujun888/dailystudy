from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.core.cache import cache
from django.core.paginator import Paginator
from goods.models import GoodsType, GoodsSKU, IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection
from order.models import OrderGoods
from redis import StrictRedis
# Create your views here.

# class Test(object):
#     def __init__(self):
#         self.name = 'abc'
#
# t = Test()
# t.age = 10
# print(t.age)
class IndexView(View):
	def get(self,request):
		#获取商品种类信息
		types = GoodsType.objects.all()
		#获取首页轮播商品信息
		goods_banners = IndexGoodsBanner.objects.all().order_by("index")
		#获取首页活动促销信息
		promotion_banners = IndexPromotionBanner.objects.all().order_by("index")
		#获取首页分类商品展示信息
		for type in types:
			#获取种类在首页分类商品的图片展示信息
			image_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by("index")
			#获取种类在首页分类商品的文字展示信息
			title_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by("index")			
			type.image_banners = image_banners
			type.title_banners = title_banners

		#用户购物车商品数目
		cart_count = 0
		user = request.user
		if user.is_authenticated:
			conn = StrictRedis(host='localhost', port=6379, db=0)
			cart_key = 'user_%d'%user.id 
			cart_count = conn.hlen(cart_key)
		#组织模板上下文
		context = {
			"types":types,
			"goods_banners":goods_banners,
			"promotion_banners":promotion_banners,
			#"type_goods_banners":type_goods_banners,
			"cart_count":cart_count
		}
		return render(request,'index.html',context)

		
	def post(request):
		pass

class ListView(View):
	def get(self,request,type_id,page):
		try:
			gtype = GoodsType.objects.get(id=type_id)
		except GoodsType.DoesNotExist:
			redirect(reverse("goods:index"))
		#获取排序方式
		sort = request.GET.get("sort")


		if sort == "price":
			skus = GoodsSKU.objects.filter(type=gtype).order_by("price")
		elif sort == "hot":
			skus = GoodsSKU.objects.filter(type=gtype).order_by("-sales")
		else:
			skus = GoodsSKU.objects.filter(type=gtype).order_by("-id")
		#所有种类信息
		types = GoodsType.objects.all()
		#对数据进行分页
		paginator=Paginator(skus,1)
		#获取第page页的内容
		try:
			page = int(page)
		except Exception as e:
			page = 1
		if page > paginator.num_pages:
			page = 1
		skus_page = paginator.page(page)
		new_skus = GoodsSKU.objects.filter(type=gtype).order_by("-create_time")[:2]
		user = request.user
		cart_count = 0
		if user.is_authenticated():
			conn = StrictRedis(host='localhost', port=6379, db=0)
			cart_key = 'user_%d'%user.id 
			cart_count = conn.hlen(cart_key)
		context = {
			"type":gtype,
			"types":types,
			"skus_page":skus_page,
			"new_skus":new_skus,
			"cart_count":cart_count,
			'skus':skus
		}

		return render(request,"list.html",context)
	def post(self,request):
		pass
# /goods/商品id
class DetailView(View):
	'''详情页'''
	def get(self, request, goods_id):
		'''显示详情页'''
		try:
			sku = GoodsSKU.objects.get(id=goods_id)
		except GoodsSKU.DoesNotExist:
			# 商品不存在
			return redirect(reverse('goods:index'))

		# 获取商品的分类信息
		types = GoodsType.objects.all()

		# 获取商品的评论信息
		sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

		# 获取新品信息
		new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

		# 获取同一个SPU的其他规格商品
		same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

		# 获取用户购物车中商品的数目
		user = request.user
		cart_count = 0
		if user.is_authenticated:
			# 用户已登录
			conn = StrictRedis(host='localhost', port=6379, db=0)
			cart_key = 'cart_%d' % user.id
			cart_count = conn.hlen(cart_key)

			# 添加用户的历史记录
			conn = StrictRedis(host='localhost', port=6379, db=0)
			history_key = 'history_%d'%user.id
			# 移除列表中的goods_id
			conn.lrem(history_key, 0, goods_id)
			# 把goods_id插入到列表的左侧
			conn.lpush(history_key, goods_id)
			# 只保存用户最新浏览的5条信息
			conn.ltrim(history_key, 0, 4)

		# 组织模板上下文
		context = {'sku':sku, 'types':types,
					'sku_orders':sku_orders,
					'new_skus':new_skus,
					'same_spu_skus':same_spu_skus,
					'cart_count':cart_count}

		# 使用模板
		return render(request, 'detail.html', context)


