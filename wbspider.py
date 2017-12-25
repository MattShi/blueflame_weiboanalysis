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
    return data_path + "/wb_seed_user_" + userid + ".txt"

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


def fb_getusersinfo(driver,listfile):
    if False == os.path.exists(data_path):
        os.mkdir(data_path)
    if False == os.path.exists(listfile):
        for user in user_list:
            fb_user_allinfo(driver,user)
    else:
        with open(listfile) as f:
            for line in f:
                if (line == "\n") | (line == "") | (line == " ") | (line == "friendlist\n"):
                    continue
                fb_user_allinfo(driver, line)
        f.close()


def fb_user_allinfo(driver,user):
    if (user == "") | (user == " "):
        return

    bID = (user.find("id=") != -1)
    user =fb_extrac_userid(user)

    f = open(data_path + "/" + user + ".txt", "w+");
    f.write(user + '\n')

    for k,v in data_type.items():

        f.write('\n')
        if bID:
            url = "https://www.facebook.com/profile.php?id=" + user + "&sk=" + v
        else:
            url = "https://www.facebook.com/" + user + "/" + v

        driver.get(url)
        driver.implicitly_wait(10)

        f.flush()
    f.close()


def fb_auto_scroll(driver,url):
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
    f.write('userids \n')
    f.write(cfginfo[0])
    f.write('\n')
    f.write(cfginfo[1])
    f.write('\n')
    return cfginfo[1]


#info
def wb_basic_info(driver,f):
    tag_name = "WB_frame_c"
    try:
        eles = driver.find_element_by_class_name(tag_name)
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
    f.write("basicinfo\n");
    url = "https://weibo.com/" + user + "/info?"
    driver.get(url)
    driver.implicitly_wait(3)

    userid = wb_user_ids(driver,f)

    wb_basic_info(driver, f)
    f.flush()

    #fans list
    f.write("fanslist\n");
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
    f.write("followlist\n");
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

    userlist = [];
    with open(path) as ff:
        for line in ff:
            if line.count('###') > 0 :
                userlist.append(line[4:-1])
        ff.close()

    for userid in userlist:
        explor_basicinfo_by_userid(driver, userid, deepth + 1, "ab+")


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
def statistic_ana_attributes():
    sta_yes = count_attributes(ana_yes_list)
    sta_no = count_attributes(ana_no_list)

    color = ['r','g']
    statistic_plot(sta_yes,'yes','r')
    statistic_plot(sta_no, 'no', 'g')


def statistic_plot(data,label,c):
    for k,v in data.items():
        unique_n, counts_n = numpy.unique(v, return_counts=True)

        pos = numpy.arange(len(unique_n))
        width = 1.0  # gives histogram aspect to the bar diagram

        ax = plt.axes()
        ax.set_xticks(unique_n)
        ax.set_xticklabels(unique_n)

        asum = sum(counts_n)
        avgfrq = [float(j) / asum for j in counts_n]

        plt.bar(pos, avgfrq, width, color=c,label=label + " "+ k)
        plt.legend(loc='upper right')
        plt.savefig(ana_data_path + "/" + k +"_" + seed_id  + label +"_.png")
        plt.clf()
        plt.cla()
        plt.close()


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


def transform_dataset(fpath,result,p = 0.7,maxc = 1000):
    #class atr1 atr2 ....
    fana = open(ana_data_set_path, "ab+")
    ftest = open(test_data_set_path,"ab+")
    rcount = 0
    with open(fpath) as f:
        for line in f:
            pos = line.find(statistic_begin_char)
            if rcount > maxc:
                break;
            rcount += 1

            if pos >= 0:
                if p > random.uniform(0, 1):
                    fana.write(result)
                    fana.write(line[pos+1:])
                else:
                    ftest.write(result)
                    ftest.write(line[pos + 1:])
    f.close()
    fana.close()
    ftest.close()


def creat_dataset(f):
    transform_dataset(ana_yes_list,'1',f)
    transform_dataset(ana_no_list,'0',f)



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
        creat_dataset(0.7)