#! python3
## WARNING ## WARNING ## WARNING ## WARNING ## WARNING ##
## This script will create a directory with over 11,000##
## html pages in the directory it is executed from!    ##
#-------------------------------------------------------------------------------
# Name:        BBC Food Recipes & Techniques
# Purpose:     Grab all the recipes from the BBC food website and
#              strip them down to basic html pages.
# Author:      Thomas Edward Rudge
#
# Created:     2016-5-17
# Copyright:   (c) Thomas Edward Rudge 2016
# Licence:     MIT
#-------------------------------------------------------------------------------


import bs4, os, requests, time, io


def get_sitemap():
    '''
    Get the BBC Food sitemap and save it to a local file.
    '''
    ## If the sitemap already exists, don't bother getting it again
    if os.path.isfile('bbc_sitemap.txt'):
        return

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
                if string.startswith('http://www.bbc.co.uk/food/recipes/'):
                    f.write(string + '\n')


def make_repodir():
    '''
    Make the repositories where the html and css files will be stored
    '''
    ## Create the location where the CSS will be stored
    cwd = os.getcwd() + os.sep

    try:
        if not os.path.isdir(cwd + 'BBC_Food_Repo'):
            os.mkdir(cwd + 'BBC_Food_Repo')
        if not os.path.isdir(cwd + 'BBC_Food_Repo' + os.sep + 'css'):
            os.mkdir(cwd + 'BBC_Food_Repo' + os.sep + 'css')
    except Exception as e:
        raise Exception(str(e))


def get_stylesheets():
    '''
    Get the stylesheets needed to display the pages properly.
    '''
    ## Get the first URL from the sitemap (assume all the pages are the same)
    with open('bbc_sitemap.txt', 'r') as f:
        url = f.readline()
    url = url.strip('\n')

    if not url:
        raise Exception('No urls found in sitemap!')

    page = None

    for attempt in range(1, 4):
        page = requests.get(url)
        try:
            page.raise_for_status()
            break
        except requests.RequestException:
            time.sleep(attempt*10)

    if not page:
        raise Exception("Couldn't retrieve page: " + url)

    soup = bs4.BeautifulSoup(page.text, 'lxml')
    sheets = []

    ## Get the sheets' urls
    for link in soup.find_all('link'):
        if 'stylesheet' in link.get('rel'):
            sheets.append(link.get('href'))

    ## Now get and save the sheets
    for link in sheets:
        link = 'http:' + link if link.startswith('//') else link
        sheet = requests.get(link)
        try:
            sheet.raise_for_status()
        except requests.RequestException:
            continue

        with io.open('BBC_Food_Repo' + os.sep + 'css' + os.sep + link.split('/')[-1], 'w', encoding='utf-8') as css:
            css.write(sheet.text)

    return sheets


def save_pages(css_links):
    '''
    Grab every web page in the BBC Food sitemap and
    save it as a local html file.
    '''
    cwd = os.getcwd()
    ## Build the new header data
    sep = os.sep
    for i, link in enumerate(css_links):
        css_links[i] = cwd + sep + 'BBC_Food_Repo' + sep + 'css' + sep + link.split('/')[-1]

    ## Cycle through the sitemap grabbing each recipe
    with open('bbc_sitemap.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            page = requests.get(line)

            try:
                page.raise_for_status()
            except requests.RequestException:
                continue

            soup = bs4.BeautifulSoup(page.text, 'lxml')
            ## Update the header
            soup.head.clear()
            for link in css_links:
                new_link = soup.new_tag('link')
                new_link.attrs['rel'] = 'stylesheet'
                new_link.attrs['href'] = link
                soup.head.append(new_link)

            ## Remove unwanted elements
            soup.header.decompose()
            decomp = [soup.find('div', class_='main-menu'),
                      soup.find('div', class_='food-wrapper'),
                      soup.find('div', class_='recipe-finder-link__wrap'),
                      soup.find('div', class_='grid-list-wrapper'),
                      soup.find('div', class_='recipe-actions'),
                      soup.find('div', class_='recipe-quick-links'),
                      soup.find('div', class_='recipe-extra-information__wrapper'),
                      soup.find('div', id='recipe-finder__box'),
                      soup.find('div', id='orb-footer'),
                      soup.find('div', id='blq-global'),
                      soup.find('a', class_='chef__image-link')]

            for noscript in soup.find_all('noscript'):
                decomp.append(noscript)
            for div in soup.find_all('div', class_='recipe-media'):
                decomp.append(div)
            for div in soup.find_all('div', class_='bbccom_display_none'):
                decomp.append(div)
            for script in soup.find_all('script'):
                decomp.append(script)

            for ele in decomp:
                if ele:
                    ele.decompose()

            ## Convert anchor tags into spans (links into text)
            tags = []
            for tag in soup.find_all('a'):
                tags.append(tag)
            for tag in tags:
                new_tag = soup.new_tag('span')
                new_tag.string = tag.text
                tag.replace_with(new_tag)

            ## Convert the soup back into html and save it to file
            html = soup.prettify()

            with io.open('BBC_Food_Repo/' + line.split('/')[-1] + '.html', 'w', encoding='utf-8-sig') as html_page:
                html_page.write(html)


def main():
    get_sitemap()
    make_repodir()
    stylesheets = get_stylesheets()
    save_pages(stylesheets)

if __name__ == '__main__':
    main()
