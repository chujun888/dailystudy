from django.conf.urls import url
from cart.views import CartDeleteView,CartAddView,CartInfoView,CartUpdateView
#from cart.views import CartAddView, CartInfoView, CartUpdateView, CartDeleteView

urlpatterns = [
	url(r'^add$',CartAddView.as_view(),name='add'),#购物车记录添加
    url(r'^$', CartInfoView.as_view(), name='show'), # 购物车页面显示
    url(r'^update$', CartUpdateView.as_view(), name='update')
    url(r'^delete$', CartDeleteView.as_view(), name='delete')

]
app_name = "cart"

#! /bin/bash
host="o2o.db.qizhuyun.com"
port="3306"
userName="o2o_admin"
password="o2o_admin1022"
dbname="qi_o2o"
dbset="--default-character-set=utf8 -A"


mysql -h${host} -u${userName} -p${password} ${dbname} -P${port}   <<  EOF

ALTER TABLE `qi_o2o_b1` RENAME TO api_log_remote_bak;
CREATE TABLE api_log_remote LIKE api_log_remote_bak;
DROP TABLE api_log_remote_bak;
ALTER TABLE api_log_remote_trans RENAME TO api_log_remote_trans_bak;
CREATE TABLE api_log_remote_trans LIKE api_log_remote_trans_bak;
DROP TABLE api_log_remote_trans_bak;
SET @schema = 'qi_o2o';
SELECT CONCAT('DROP TABLE ',GROUP_CONCAT(CONCAT(@schema,'.',table_name)),';')
INTO @droplike
FROM information_schema.tables
WHERE  TABLE_SCHEMA = @schema AND (table_name LIKE 'api_log_remote_2%' OR table_name LIKE 'api_log_remote_trans_2%');
SELECT @droplike;
PREPARE stmt FROM @droplike;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

EOF



      