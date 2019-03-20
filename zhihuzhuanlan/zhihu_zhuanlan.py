import time
import re
import os
import requests
from bs4 import BeautifulSoup


def get_list():
    url = '''https://zhuanlan.zhihu.com/api/columns/{author}/articles?include=data%5B*%5D.admin_closed_comment%2Ccomment_count%2Csuggest_edit%2Cis_title_image_full_screen%2Ccan_comment%2Cupvoted_followees%2Ccan_open_tipjar%2Ccan_tip%2Cvoteup_count%2Cvoting%2Ctopics%2Creview_info%2Cauthor.is_following%2Cis_labeled%2Clabel_info'''.replace(
        "{author}", author)
    article_dict = {}
    while True:
        print('fetching', url)
        try:
            resp = requests.get(url, headers=headers)
            j = resp.json()
            data = j['data']
        except:
            print('get list failed')

        for article in data:
            aid = article['id']
            akeys = article_dict.keys()
            if aid not in akeys:
                article_dict[aid] = article['title']

        if j['paging']['is_end']:
            break
        url = j['paging']['next']
        url = url.replace("zhuanlan.zhihu.com/columns/", "zhuanlan.zhihu.com/api/columns/")
        time.sleep(2)

    with open('zhihu_ids.txt', 'w') as f:
        items = sorted(article_dict.items())
        for item in items:
            f.write('%s %s\n' % item)


def get_html(aid, title, index):
    title = title.replace('/', '／')
    title = title.replace('\\', '＼')
    file_name = '%03d. %s.html' % (index, title)
    if os.path.exists(file_name):
        print(title, 'already exists.')
        return
    else:
        print('saving', title)
    try:
        url = 'https://zhuanlan.zhihu.com/p/' + aid
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        # for tag in soup.find_all("figure")[-2:]:
        #     tag.decompose()
        content = soup.find(class_='Post-RichText').prettify()
        content = content.replace('data-actual', '')
        content = content.replace('h1>', 'h2>')
        content = re.sub(r'<noscript>.*?</noscript>', '', content)
        content = re.sub(r'src="data:image.*?"', '', content)
        content = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><h1>%s</h1>%s</body></html>' % (
            title, content)
        with open(file_name, 'w', encoding="utf-8") as f:
            f.write(content)
    except Exception as ex:
        print(ex)
        print('get %s failed', title)
    time.sleep(2)


def get_details():
    with open('zhihu_ids.txt') as f:
        i = 1
        for line in f:
            lst = line.strip().split(' ')
            aid = lst[0]
            title = '_'.join(lst[1:])
            get_html(aid, title, i)
            i += 1


def to_pdf():
    import pdfkit
    print('exporting PDF...')
    htmls = []
    for root, dirs, files in os.walk('.'):
        htmls += [name for name in files if name.endswith(".html")]
    config = pdfkit.configuration(wkhtmltopdf=path_wk)
    pdfkit.from_file(sorted(htmls), author + '.pdf', configuration=config)


if __name__ == '__main__':
    author = input('Please input author name:(default crossin)')
    path_wk = input(r'Please input wkhtmltopdf path:(default C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe)')
    if not author:
        author = 'crossin'
    if not path_wk:
        path_wk = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # 安装位置
    headers = {
        'origin': 'https://zhuanlan.zhihu.com',
        'referer': 'https://zhuanlan.zhihu.com/%s' % author,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000',
    }
    get_list()
    get_details()
    to_pdf()
