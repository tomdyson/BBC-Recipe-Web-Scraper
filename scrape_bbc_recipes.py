#! python3
## WARNING ## WARNING ## WARNING ## WARNING ## WARNING ##
## This script will create a directory with over 11,000##
## html pages in the directory it is executed from!    ##
#-------------------------------------------------------------------------------
# Name:        BBC Food Recipes & Techniques
# Purpose:     Grab all the recipes and techniques
#              the BBC food website
# Author:      Thomas Edward Rudge
#
# Created:     2016-5-17
# Copyright:   (c) Thomas Edward Rudge 2016
# Licence:     MIT
#-------------------------------------------------------------------------------


import bs4, os, requests, time


def get_sitemap():
    '''
    Get the BBC Food sitemap and save it to a local file.
    '''
    page = None

    for attempt in range(1, 4):
        page = requests.get('http://www.bbc.co.uk/food/sitemap.xml')
        try:
            page.raise_for_status()
            break
        except requests.RequestException:
            time.sleep(attempt*10)

    if not page:
        raise Exception('Failed to get sitemap.xml')

    sitemap = bs4.BeautifulSoup(page.text, 'xml')

    with open('bbc_sitemap.txt', 'w') as f:
        for line in sitemap.find_all('loc'):
            for string in line.stripped_strings:
                if string.startswith('http://www.bbc.co.uk/food/recipes/') or\
                   string.startswith('http://www.bbc.co.uk/food/techniques/'):

                    f.write(string + '\n')


def save_pages():
    '''
    Grab every web page in the BBC Food sitemap and
    save it as a local html file.
    '''

    cwd = os.getcwd()

    if not os.path.isdir(cwd + '\\BBC_Food_Repo'):
        os.mkdir(cwd + '\\BBC_Food_Repo')

    with open('bbc_sitemap.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            page = requests.get(line)

            try:
                page.raise_for_status()
            except requests.RequestException:
                continue

            with open('BBC_Food_Repo/' + line.split('/')[-1] + '.html', 'w', encoding='utf8') as html_page:
                html_page.write(page.text)


def main():
    get_sitemap()

    save_pages()


if __name__ == '__main__':
    main()
