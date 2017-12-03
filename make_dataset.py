import pandas as pd
import numpy as np
from requests import get
from bs4 import BeautifulSoup
from time import sleep, time
from random import randint
from warnings import warn
from IPython.core.display import clear_output
from selenium import webdriver
import lxml

def get_browser_url_reponse(url, param):
    url_git = url.format(param)
    browser.get(url_git)
    return browser

def get_value(soup, select, *args):
    value = soup.select(select)  
    if args:
        return int(''.join(filter(str.isdigit, value[args[0]].text)))
    else:
        return int(''.join(filter(str.isdigit, value[0].text))) 

def is_empty(soup, select, *args):
    value = soup.select(select)    
    if(len(value)==0):
        return True
    else:
        return False

df_repos = pd.read_csv('repo_fullname_list.csv')
full_names = df_repos['Nome_do_repositorio']

git_stats = pd.DataFrame(columns=['full_name', 'commits', 'branches', 'releases', 'watchers', 'forks', 'issues_open',
                                  'issues_closed', 'stars'])

requests = 0
start_time = time()
elapsed_time = 0

browser = webdriver.PhantomJS(executable_path=r'./phantomjs', service_args=['--ignore-ssl-errors=true'])

for i in np.arange(0, len(full_names)):   
    
    browser = get_browser_url_reponse('http://www.github.com/{}', full_names[i])
    sleep(randint(1,6))
    soup = BeautifulSoup(browser.page_source, 'lxml')

    requests += 1
    elapsed_time = time() - start_time
    print('Request:{}; Repo:{}; Frequency: {} requests/s'.format(requests, full_names[i], requests/elapsed_time))
    clear_output(wait = True)

    if not is_empty(soup, "div.overall-summary.overall-summary-bottomless"):
        commits = get_value(soup, "li.commits span.num")
        branches = get_value(soup,"a[href='/"+full_names[i]+"/branches'] span.num")
        releases = get_value(soup, "a[href='/"+full_names[i]+"/releases'] span.num")
        watchers = get_value(soup, "a[href='/"+full_names[i]+"/watchers']")
        forks = get_value(soup, "a[href='/"+full_names[i]+"/network']")
        stars = get_value(soup, "a[href='/"+full_names[i]+"/stargazers']")
    
        url_git_issues = 'http://www.github.com/{}/issues'
        browser = get_browser_url_reponse(url_git_issues, full_names[i])
        soup = BeautifulSoup(browser.page_source, 'lxml')
    
        if(not is_empty(soup, 'div.issues-listing div.table-list-filters a', 0)):
            issues_open = get_value(soup, 'div.issues-listing div.table-list-filters a', 0)
        else:
            issues_open = 0
        
        if(not is_empty(soup, 'div.issues-listing div.table-list-filters a', 1)):
            issues_closed = get_value(soup, 'div.issues-listing div.table-list-filters a', 1)
        else:
            issues_closed = 0
    
        git_stats.loc[i] = [full_names[i], commits, branches, releases, watchers, forks, issues_open, issues_closed, stars]
    
git_stats.to_csv('git_stats.csv')    
