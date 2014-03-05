#Weibo_spider contents

**This file is the record of weibo data structures and page style**

###About URL

1. The home page URL
    
    > http://weibo.com/p/1004061705586121/weibo

2. URL of weibo content

    > http://weibo.com/p/1004061705586121/weibo?page=2

    With a page-argument you can access the specific content page.
    
    **Note:**every page on weibo.com now display 15 messages per time,
    if you want to get the rest messages in the page ,you have to build
    a XHR request to access them.

3. URL of full content access in a page.
    
    > http://weibo.com/p/aj/mblog/mbloglist?domain=100406&pre_page=2&page=2&max_id=3676930857883576&end_id=3680528530503370&count=15&pagebar=1&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__21&id=1004061705586121&script_uri=/p/1004061705586121/weibo&feed_type=0&__rnd=1394021493391
    
    >**the data structure of the request**
    ```html
        __rnd	1394021493391
        count	15
        domain	100406
        end_id	3680528530503370
        feed_type	0
        filtered_min_id	
        id	1004061705586121
        max_id	3676930857883576
        max_msign	
        page	2
        pagebar	1
        pl_name	Pl_Official_LeftProfileFeed__21
        pre_page	2
        script_uri	/p/1004061705586121/weibo
    ```
