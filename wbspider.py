# -*- coding: utf-8 -*-

import sys
import time
import os
import os.path
import numpy
import random

from selenium import webdriver
from bs4 import BeautifulSoup

import matplotlib.pyplot as plt
import plotly.plotly as py

###########################
##user : like list /forward list/ weibo list/
###########################


user_list = ["chandrasekar1994","nevillegoutham","realtorbeeler","bridget.ross.779","Gangster.trinh","mie.duen.5","shreepal.patel.1","shrirang.vidhale"
             ,"RUSHIrushi","nidhi.parmar.1848816","ngduffy","charlene.logue.9","BhargavSai.D","siddharth.ganesh.7","vivekmani","ramprakash.deva246"]

data_path = "data"
ana_data_path = "data/analysis"
max_deepth = 1
debug_print = 1
seperate_str = "###"
statistic_begin_char = ":"
seed_id = "2485659250"
seed_user_info_path = data_path + "/wb_seed_user_" + seed_id + ".txt"
ana_yes_list = ana_data_path + "/" + seed_id + "_" +"analysisresult_yes.txt"
ana_no_list = ana_data_path + "/" + seed_id + "_" +"analysisresult_no.txt"
ana_data_set_path = ana_data_path +  "/" + seed_id + "_" +"analysis_dataset.txt"
test_data_set_path = ana_data_path +  "/" + seed_id + "_" +"test_dataset.txt"


data_type = {"tvshow":"tv","music":"music","checkin":"map","group":"groups","friendlist":"friends"
        ,"likelist":"likes","educationandwork":"about?section=education","movie":"movies","livein":"about?section=living","sport":"sports"}

#####################################################################
def getcfginfo(driver):
    html_source = driver.page_source
    str_ps = html_source.find("$CONFIG['uid']")
    str_pe = html_source.find(";",str_ps)
    u_id = html_source[str_ps+16:str_pe-1]
    str_ps = html_source.find("$CONFIG['oid']='")
    str_pe = html_source.find(";", str_ps)
    o_id = html_source[str_ps + 16: str_pe - 1]
    return (u_id,o_id)


def getuserinfofilepath(userid):
    return data_path + "/wb_user_info" + userid + ".txt"


def getuserpostsfilepath(userid):
    return data_path + "/wb_user_posts" + userid + ".txt"


def extractnumber(s):
    ns = ""
    for c in s:
        if c  <= '9' and c >= '0':
            ns += c
    return ns


def extractnumbers(s):
    nums = []

    ns = ""
    for c in s:
        if c  <= '9' and c >= '0':
            ns += c
        else:
            if(len(ns) > 0):
                nums.append(ns)
            ns = ""
    return nums



def scroll(driver):
    driver.execute_script("""   
           (function () {   
               var y = document.body.scrollTop;   
               var step = 1000;   
               window.scroll(0, y);   

               function f() {   
                   if (y < document.body.scrollHeight) {   
                       y += step;   
                       window.scroll(0, y);   
                       setTimeout(f, 100);   
                   }  
                   else {   
                       window.scroll(0, y);   
                       document.title += "scroll-done";   
                   }   
               }   

               setTimeout(f, 1000);   
           })();   
           """)


def auto_scroll(driver,url):
    bauto = True
    last_height = driver.execute_script("return document.body.scrollHeight")
    bValid = (driver.current_url == url)
    while(bauto):
        driver.execute_script("window.scroll(0, document.body.scrollHeight+1000);")
        time.sleep(2)
        if url != driver.current_url:
            bValid = False
            break;

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return bValid


def wb_user_ids(driver,f):
    cfginfo = getcfginfo(driver)
    f.write('#userids \n')
    f.write(cfginfo[0])
    f.write('\n')
    f.write(cfginfo[1])
    f.write('\n')
    return cfginfo[1]


#info
def wb_basic_info(driver,f):
    tag_name_d = "WB_frame_c"
    tag_name_c = "PCD_counter"
    try:
        #fans weibo follow number
        eles = driver.find_element_by_class_name(tag_name_c)
        data_soup = BeautifulSoup(eles.get_attribute("innerHTML"), "html5lib")
        f.write("##numbers\n")
        lists = data_soup.find_all("td")
        for lt in lists:
            f.write(extractnumber(lt.text.replace('\t','')))
            f.write('\n');

        #detail
        f.write("##detail\n")
        eles = driver.find_element_by_class_name(tag_name_d)
        data_soup = BeautifulSoup(eles.get_attribute("innerHTML"), "html5lib")

        lists = data_soup.find_all("li")
        for lt in lists:
            f.write(lt.text.replace('\t',''))
            f.write('\n');


    except Exception as e:
        print ("likelist ")
        print ("Exception found", format(e))



#analysis friends
def wb_fansorfollow_list(driver, f):
    user_lists = "uidList"
    try:
        val = driver.find_element_by_name(user_lists).get_attribute("value")
        ids = val.split(",")
        for id in ids:
            f.write("####"+id)
            f.write('\n');

        val = driver.find_element_by_name('mp').get_attribute("value")
        return int(val)

    except Exception as e:
        print ("friendlist ")
        print ("Exception found", format(e))
        return 0


def fb_extract_friendname(str):
    s1 = str.find("\"Add ")
    s2 = str.find(" as a friend")
    return str[s1+5:s2]


def fb_extrac_link(str):
    s1 = str.find("href=\"")
    s2 = str.find("?fref",s1)
    if s2 <= s1:
        s2 = str.find("&amp;fref",s1)
    return str[s1 + 6:s2]


def fb_extrac_userid(str):
    s1 = str.find("com/")
    s2 = str.find("=",s1)
    if s2 != -1:
        return str[s2+1:-1]
    return str[s1 + 4:s2]


###############################################################################################
def network_login(username, password, userid):

    url = "http://www.weibo.com/login.php"
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    driver.implicitly_wait(10)
    userui = driver.find_element_by_id('loginname')
    userui.clear()
    userui.send_keys(username)
    pswui = driver.find_element_by_name('password')
    pswui.clear()
    pswui.send_keys(password)
    driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()

    explor_basicinfo_by_userid(driver, userid, 0, "wb")
    driver.quit()



def explor_basicinfo_by_userid(driver, user, deepth, mode):
    if (user == "") | (user == " "):
        return
    if(deepth > max_deepth):
        return

    path = getuserinfofilepath(user)
    f = open(path, mode);
    f.write('\n')


    #basic info
    f.write("#basicinfo\n");
    url = "https://weibo.com/" + user + "/info?"
    driver.get(url)
    driver.implicitly_wait(3)

    userid = wb_user_ids(driver,f)

    wb_basic_info(driver, f)
    f.flush()

    #fans list
    f.write("#fanslist\n");
    n_page = 1
    ncur_page = 0
    while ncur_page < n_page:
        url = "https://weibo.cn/" + user + "/fans?page="+str(ncur_page+1)
        driver.get(url)
        driver.implicitly_wait(1)
        n_page = wb_fansorfollow_list(driver, f)
        if n_page <= 0:
            break;
        ncur_page += 1
        f.flush()

    #follow list
    f.write("\n");
    f.write("#followlist\n");
    n_page = 1
    ncur_page = 0
    while ncur_page < n_page:
        url = "https://weibo.cn/" + user + "/follow?page="+str(ncur_page+1)
        driver.get(url)
        driver.implicitly_wait(1)
        n_page = wb_fansorfollow_list(driver, f)
        if n_page <= 0:
            break;
        ncur_page += 1
        f.flush()

    f.close()

    #post list
    explor_postinfo_by_userid(driver,userid)

    userlist = [];
    with open(path) as ff:
        for line in ff:
            if line.count('###') > 0 :
                userlist.append(line[4:-1])
        ff.close()

    for userid in userlist:
        explor_basicinfo_by_userid(driver, userid, deepth + 1, "ab+")


def explor_postinfo_by_userid(driver,uid):
    path = getuserpostsfilepath(uid)
    f = open(path, "ab+");
    f.write('\n')

    npageidx = 1
    while(npageidx < 20):
        url = "https://weibo.com/u/"+ uid + "?profile_ftype=1&is_all=1&page=" + str(npageidx)
        driver.get(url)
        driver.implicitly_wait(3)
        auto_scroll(driver,url)

        try:

            posts_tag = "WB_frame_c"
            post_cls = "WB_feed_detail clearfix"
            post_statistic="WB_feed_handle"

            # fans weibo follow number
            eles = driver.find_element_by_class_name(posts_tag)
            data_soup = BeautifulSoup(eles.get_attribute("innerHTML"), "html5lib")
            f.write("\n")
            ls_detail = data_soup.findAll("div", class_="WB_cardwrap WB_feed_type S_bg2 WB_feed_like ")
            for ls in ls_detail:
                f.write(ls.contents[1].contents[5].contents[3].contents[1].attrs['title'])#time
                f.write(" #")
                f.write(ls.contents[1].contents[5].contents[3].contents[3].contents[0])#device
                f.write(" #")
                nums = extractnumbers(ls.contents[3].text.replace('\n', ' '))
                for num in nums:
                    f.write(num)
                    f.write("#")
                f.write('\n');

        except Exception as e:
            print ("posts ")
            print ("Exception found", format(e))
        npageidx+=1
    f.close()





################################################################################################
def comm_create_userlist():
    path = seed_user_info_path
    user_list[:] = [];
    with open(path) as f:
        for line in f:
            if line == "friendlist\n":
                continue

            user = fb_extrac_userid(line)
            if (user != "") & (user != " "):
                user_list.append(fb_extrac_userid(line))
    f.close()

#analysis data
def ana_friends_comm():

    comm_create_userlist()

    for i in range(0,len(user_list)):
        for j in range(0,len(user_list)):
            if i != j:
                find_comm_simple(user_list[i],user_list[j])


def find_comm_simple(user1,user2):
    if False == os.path.exists(ana_data_path):
        os.mkdir(ana_data_path)

    useinfo1 = read_user_file(user1)
    useinfo2 = read_user_file(user2)

    bfriends = check_is_friend(user1, useinfo2["friendlist"])
    if bfriends:
        fana = open(ana_yes_list, "ab+")
    else:
        fana = open(ana_no_list, "ab+")

    fana.write("result " + user1 + "_" + user2 + ":")
    for k in useinfo1.keys():
        if (useinfo1[k] is not None) & (useinfo2[k] is not None):
            sameitems = set(useinfo1[k]).intersection(useinfo2[k])
            if sameitems is not None:
                fana.write(" " + str(len(sameitems)))
            else:
                fana.write(" 0")
        else:
            fana.write(" 0")

    fana.write("\n")
    fana.flush()
    fana.close()


def find_comm(user1,user2):
    if False == os.path.exists(ana_data_path):
        os.mkdir(ana_data_path)

    useinfo1 = read_user_file(user1)
    useinfo2 = read_user_file(user2)

    bfriends =  check_is_friend(user1,useinfo2["friendlist"])
    if bfriends:
        fana = open(ana_yes_list, "ab+")
    else:
        fana = open(ana_no_list, "ab+")

    fana.write("\n result \n")
    fana.write(user1 + "_" + user2 + '\n')

    for k in useinfo1.keys():
        fana.write(k + " ")
        if (useinfo1[k] is not None) & (useinfo2[k] is not None):
            sameitems = set(useinfo1[k]).intersection(useinfo2[k])
            if sameitems is not None:
                fana.write(str(len(sameitems)) + "###")
                for item in sameitems:
                    fana.write(item + " ")
                fana.write("\n")
            else:
                fana.write("0" + "\n")
        else:
            fana.write("0" + "\n")

    fana.flush()
    fana.close()


def check_is_friend(userid,friendslist):
    if friendslist is None:
        return False

    for user in friendslist:
        if user.find(userid) >= 0:
            return True;
    return False


def read_user_file(user):
    userinfo = dict.fromkeys(data_type)

    path = data_path + "/" + user + ".txt"
    if False == os.path.exists(path):
        print path + " NOT EXIST"
        return userinfo

    with open(path) as f:
        lastkey = ""
        for line in f:
            line = line[:-1]
            if (line == user) | (line == " ") | (line == ""):
                continue
            if data_type.keys().count(line) > 0:
                lastkey = line
            else:
                if userinfo[lastkey] is  None:
                    userinfo[lastkey] = []
                userinfo[lastkey].append(line.lower())
    f.close()
    return userinfo


##########################################################################
#statistic analysis

def count_attributes(fpath):
    statinfo = dict.fromkeys(data_type)

    for k in statinfo.keys():
        if statinfo[k] is None:
            statinfo[k] = []
    knum = len(statinfo.keys())

    rcount = 0
    with open(fpath) as f:
        for line in f:
            pos = line.find(statistic_begin_char)
            if pos >= 0:
                attrs = line[pos+1:-1].split()
                if(len(attrs) == knum):
                    idx = 0

                    for k in statinfo.keys():
                        statinfo[k].append(int(attrs[idx]))
                        idx += 1
                else:
                    print ("Exception found", str(attrs))
    f.close()

    return statinfo



if __name__ == '__main__':
    try:
        reload(sys)
        sys.setdefaultencoding('utf8')

        username = sys.argv[1]
        password = sys.argv[2]
        if len(sys.argv) >= 3:
            seed_id = sys.argv[3]
    except IndexError:
        print 'Usage: %s <username> <password> <id>' % sys.argv[0]
    else:

        network_login(username, password, seed_id)
        #fb_spider(username, password, friend_list_path)
        #ana_friends_comm()
        #statistic_ana_attributes()
