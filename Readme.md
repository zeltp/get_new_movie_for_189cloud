## 自动转存最新剧集
### 此脚本针对最新的剧集进行保存,非直接资源同步
### 垃圾代码,估计入门级都算不上 

###  运行逻辑:

判断剧集是否有更新→匹配网盘的文件进行转存

匹配的文件只会比匹配数据库集数新的文件进行保存


### 测试运行环境：
Python == 3.6.8</br>

selenium == 3.141.0</br>

numpy == 1.19.5</br>

cn2an == 0.5.22</br>

PyMySQL == 1.0.2</br>

### 使用方法</br>

将init.sql导入到数据库</br>

修改文件中的用户名密码及数据库链接</br>

然后直接运行即可</br>

<code> python3 update_movie.py</code>

### 添加要更新的剧集

添加要更新的电视剧或动漫到数据库   字段如下：</br>

Name 为名字</br>

movie_info 为播放页面的url(目前匹配了腾讯视频，爱奇艺，优酷，哔哩哔哩)</br>

update_url 为资源更新的地址（有提取码时，如果地址未带有则需要填写到share_key字段）</br>

Share_key 为资源的分享码</br>

url_path 为资源的二级目录名称，如果有三级目录，用/分割，如果没有直接留空即可</br>

save_path 为保存路径，默认会加脚本内的前置默认路径，如果需要指定完整路径则用/开头写路径</br>

have_episodes 为网盘现有集数，默认为0</br>

Update_time 为最新集数的上次更新时间，默认即可</br>

url_status 为资源地址的状态，默认1即可，后续资源地址失效时会自动改为0，更新资源后手动改1</br>

update_interval  为更新最新集数间隔的天数，默认即可,电视剧会自动更新为1,其他为7</br>  

latest_episodes 为最新的集数（默认0即可，会自动更新）</br>
