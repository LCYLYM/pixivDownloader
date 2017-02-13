# PixivDownloader
Pixiv And Pixivision Illustrations Crawler And Downloader.<br>
 
* 项目主要用于 Pixiv站和Pixivision的插画特辑信息爬取和图片下载<br>
	支持图片质量：原图|大图下载<br>
      	支持以下下载方式：<br>
           1.  Pixivision插画特辑列表页全部爬取<br>
          2.  Pixivision插画特辑详情页全部爬取<br>
          3.  通过Pixiv插画url下载<br>
          4.  通过Pixiv插画ID下载<br>
          5.  通过Pixiv插画ID下载关联作品<br>
          6.  通过关键字搜索下载<br>
 
* 核心配置文件__pixiv_config.py__<br>
     1. 修改__CRAWLER_HEADER__中__Accept-Language__，获取4中不同语言的特辑描述。<br>
     2. 修改__IMAGE_SVAE_BASEPATH__，指定图片存储位置。<br>
     3. 修改__IMAGE_QUALITY__，指定下载的图片质量。<br>
     4. 修改__USE_FILTER__，True：启动RedisFilter，自动过滤重复下载的特辑。False:重复下载特辑会覆盖原文件。<br>
     *. 更多详细配置请看文件注释。

运行菜单：
~~~
python  launcher.py 
~~~
运行Pixivision全站插画爬虫:
（全站爬取完毕后，如果Pixivsion有更新，可以修改配置文件中的PAGE_NUM为更新的页数，比如Pixivsion有2页更新未爬取，修改PAGE_NUM=2,全站插画爬虫则会爬取前2页的所有特辑）
~~~
python launcher_plus.py
~~~
运行Pixivision全站插画爬虫补全脚本：
~~~
python launcher_check_completion.py
~~~
启动关联下载，通过Pixiv插画id下载关联作品,自定义关联深度，每次向下关联可获取20-30副插画，因为越向下关联性越差，质量也会变低，因此关联深度不能设置太大。
~~~
python launcher_related.py
~~~
启动搜索下载，自动下载Pixiv通过关键字搜索到插画。需要输入或设置：Pixiv邮箱或ID，Pixiv密码,搜索关键字，存储路径，爬取页数，下载的插画的最小收藏数。
~~~
python launcher_search.py
~~~

实现思路：参考我的博客文章[shawblog.me](https://shawblog.me/blog/112.html)<br>

PS①:因网络问题，下载失败很难避免。运行完毕后，若有提示下载失败的插画，可以通过查看download_error.log文件获取下载失败的插画详情。运行launcher.py 选择使用url或ID补充下载。<br>

PS②:关于搜索下载，在没有会员的情况下，很难搜到高质量的人气作品。<br>
&nbsp;&nbsp;&nbsp;&nbsp;网上的做法：在关键字后加 1000users入り ，即1000以上用户收藏，表示搜索tag中或描述中包含关键字1000users入り，1000可替换为其他数值。这样搜出来的作品的确能保证是人气作品，但只对大类名有效（比如東方project,艦これ 这类搜索）且会遗漏很多优秀作品,小类名的作品则会一幅都搜不出。<br>
&nbsp;&nbsp;&nbsp;&nbsp;在使用小类目搜索下载时，你可以尝试一下方法下载人气作品：<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.增加爬取页数。 <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.适当调整配置参数“DOWNLOAD_THRESHOLD”即_下载的插画的最小收藏数_的设置。<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.减小搜索关键字范围。 <br>

PS③:因python2的编码问题。如果出现了在控制台输入中文||日文出现字符编码异常情况，请设置控制台运行环境字符编码为UTF-8后重试。
