# -*- coding: utf-8 -*-

import urllib.request
import json
import time
import datetime
import random

#定义要爬取的微博大V的微博ID
id='6006394101'

#设置代理IP 可以从 http://www.xicidaili.com/nn/1  查找可用的代理IP与端口
proxy_addr="175.155.138.182:1133"

#定义页面打开函数
def use_proxy(url,proxy_addr):
    req=urllib.request.Request(url)
    req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
    proxy=urllib.request.ProxyHandler({'http':proxy_addr})
    opener=urllib.request.build_opener(proxy,urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    data=urllib.request.urlopen(req).read().decode('utf-8','ignore')
    return data

#获取微博主页的containerid，爬取微博内容时需要此id
def get_containerid(url):
    data=use_proxy(url,proxy_addr)
    content=json.loads(data).get('data')
    tabs = content.get('tabsInfo').get('tabs')
    for data in tabs:
        if(data.get('tab_type')=='weibo'):
            containerid=data.get('containerid')
    return containerid

#获取微博大V账号的用户基本信息，如：微博昵称、微博地址、微博头像、关注人数、粉丝数、性别、等级等
def get_userInfo(id):
    url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+id
    data=use_proxy(url,proxy_addr)
    content=json.loads(data).get('data')
    profile_image_url=content.get('userInfo').get('profile_image_url')
    description=content.get('userInfo').get('description')
    profile_url=content.get('userInfo').get('profile_url')
    verified=content.get('userInfo').get('verified')
    guanzhu=content.get('userInfo').get('follow_count')
    name=content.get('userInfo').get('screen_name')
    fensi=content.get('userInfo').get('followers_count')
    gender=content.get('userInfo').get('gender')
    urank=content.get('userInfo').get('urank')
    print("微博昵称："+name+"\n"+"微博主页地址："+profile_url+"\n"+"微博头像地址："+profile_image_url+"\n"+"是否认证："+str(verified)+"\n"+"微博说明："+description+"\n"+"关注人数："+str(guanzhu)+"\n"+"粉丝数："+str(fensi)+"\n"+"性别："+gender+"\n"+"微博等级："+str(urank)+"\n")

#获取 某条微薄展开后的 的全部内容:微薄字数超过一定数量就被折叠起来了必须再get
def getDetailContent(detail_url):
    try:
        data=use_proxy(detail_url,proxy_addr)
        data2 = data.split('var $render_data =')[1].split('var __wb_performance_data')[0]
        data3 = data2.replace('[0] || {};','')
        #print( data3)
        content=json.loads(data3)[0]['status']['text']
        content=content.replace('<br>',' ').replace('<br />',' ')
        #print (content)
        return content
    except Exception as e:
        print(e)
        return ''
    
#版本2比上一个getDetailContent 硬分 要省力
def get_detailContent(detail_url):
    try:
        data=use_proxy(detail_url,proxy_addr) 
        if not data.find('微博正文 - 微博HTML5版'):
            return '[该条已经被和谐咯] '
        content = json.loads(data).get('data')
        longTextContent=content.get('longTextContent')
        return longTextContent
    except Exception as e:
        print(e)
        return ''
    
#获取微博内容信息,并保存到文本中，内容包括：每条微博的内容、微博详情页面地址、点赞数、评论数、转发数等
def get_weibo(id,file):
    count = 0
    i=1
    while True:
        url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+id
        weibo_url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+id+'&containerid='+get_containerid(url)+'&page='+str(i)
        try:
            data=use_proxy(weibo_url,proxy_addr)
            content = json.loads(data).get('data')            
            cards=content.get('cards')
            cards_len = len(cards)
            if(cards_len>0):
                for j in range(cards_len-1):
                    print("-----正在爬取第"+str(i)+"页，第"+str(j+1)+"条微博------")
                    card_type=cards[j].get('card_type')
                    if(card_type==9):
                        mblog=cards[j].get('mblog')
                        attitudes_count=mblog.get('attitudes_count')
                        comments_count=mblog.get('comments_count')
                        created_at=mblog.get('created_at')
                        reposts_count=mblog.get('reposts_count')
                        scheme=cards[j].get('scheme')
                        isLongText = bool(mblog.get('isLongText'))
                        if (not isLongText):
                            text=mblog.get('text')
                        else:
                            idstr = mblog.get('idstr')
                            detail_url = 'https://m.weibo.cn/statuses/extend?id='+str(idstr)
                            text = get_detailContent(detail_url)
                        if len(text)<0:
                            continue
                        count = count + 1
                        with open(file,'a',encoding='utf-8') as fh:
                            fh.write("----第"+str(i)+"页，第"+str(j+1)+"条微博----"+"\n")
                            fh.write("微博地址："+str(scheme)+"\n"+"发布时间："+str(created_at)+"\n"+"微博内容："+text+"\n"+"点赞数："+str(attitudes_count)+"\n"+"评论数："+str(comments_count)+"\n"+"转发数："+str(reposts_count)+"\n")
                i+=1
                if( i%12 == 0):
                    sleeptime = random.randint(1,5)
                    time.sleep(sleeptime)
            else:
                break
        except Exception as e:
            print(e)
            pass
    print('>>>>>>>>>>>>>>>>>>>')
    print('共计：%s'%count)

if __name__=="__main__":
    id_list = ['1852299857','101174']
    for id in id_list:
        file=id+ "%s.txt"%datetime.datetime.now().strftime('[%Y-%m-%d %H %M %S]')
        get_userInfo(id)
        get_weibo(id,file)

    

