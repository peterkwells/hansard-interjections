from bs4 import BeautifulSoup
import bs4
import os
import re
import datetime
from pymongo import MongoClient
from PIL import Image, ImageOps

from credentials import MONGO_URL

XML_DIR = os.path.join(os.path.dirname(__file__), 'xml')
IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'images')


def get_speaker_details(interjection):
    speaker = {}
    details = []
    talker = interjection.find('talk.start').find('talker')
    speaker['name'] = talker.find('name', role='display').string.encode('utf-8')
    try:
        speaker['fullname'] = talker.find('name', role='metadata').string.encode('utf-8')
    except AttributeError:
        pass
    # speaker['page'] = talk.talker.find('page.no').string.encode('utf-8')
    speaker['id'] = talker.find('name.id').string
    fields = ['role', 'electorate', 'party']
    for field in fields:
        try:
            details.append(talker.find(field).string.encode('utf-8'))
        except AttributeError:
            pass
    speaker['details'] = ' &middot; '.join(details)
    return speaker


def find_interjections(house):
    dbclient = MongoClient(MONGO_URL)
    db = dbclient.get_default_database()
    xml_path = os.path.join(XML_DIR, house)
    dirs = [d for d in os.listdir(xml_path) if (os.path.isdir(os.path.join(xml_path, d)) and d != 'missing')]
    for directory in dirs:
        current_path = os.path.join(xml_path, directory)
        files = [f for f in os.listdir(current_path) if f[-4:] == '.xml']
        # with open(os.path.join(md_path, 'index.md'), 'w') as index_file:
        #    write_frontmatter(index_file, directory)
        for file in files:
            interjections = []
            with open(os.path.join(current_path, file), 'rb') as xml_file:
                soup = BeautifulSoup(xml_file.read(), 'lxml')
                header = soup.find('session.header')
                date = header.date.string.strip()
                print date
                year, month, day = date.split('-')
                for index, debate in enumerate(soup.find_all('debate')):
                    debate_title = debate.debateinfo.title.string.strip().encode('utf-8')
                    if debate_title == 'QUESTION':
                        try:
                            subtitle = debate.find('subdebateinfo').find('title').string.strip().encode('utf-8')
                            debate_title = '{}: {}'.format(debate_title, subtitle)
                        except AttributeError:
                            pass
                    debate_url = 'https://historichansard.net/{}/{}/{}/#debate-{}'.format(house, year, file[:-4], index)
                    for interjection in debate.find_all('interjection'):
                        speaker = get_speaker_details(interjection)
                        if interjection.find('para'):
                            text = interjection.find('para').get_text()
                            text = re.sub(r'^[\s\-]*', '', text)
                            text = re.sub(r'\s+', ' ', text)
                            text = re.sub(r'\s+([\.\?\!]+)', r'\1', text)
                            text = re.sub(r'\s+1\s*$', r'?', text)
                            length = len(text)
                            interjection = {
                                'house': house,
                                'date': datetime.datetime(int(year), int(month), int(day)),
                                'year': int(year),
                                'debate': debate_title,
                                'url': debate_url,
                                'speaker': speaker,
                                'text': text,
                                'length': length
                            }
                            interjections.append(interjection)
                print '{} interjections'.format(len(interjections))
                if interjections:
                    db.interjections.insert_many(interjections)
                    # print interjections


def add_fullnames():
    dbclient = MongoClient(MONGO_URL)
    db = dbclient.get_default_database()
    for interjection in db.interjections.find({'speaker.fullname': {'$exists': False}}):
        print interjection['speaker']['name']
        speaker = db.interjections.find_one({'speaker.id': interjection['speaker']['id'], 'speaker.fullname': {'$exists': True}})
        try:
            db.interjections.update_one({'_id': interjection['_id']}, {'$set': {'speaker.fullname': speaker['speaker']['fullname']}})
        except TypeError:
            print interjection['speaker']['id']


def top_interjectors():
    dbclient = MongoClient(MONGO_URL)
    db = dbclient.get_default_database()
    pipeline = [
        {'$group': {'_id': '$speaker.id', 'total': {'$sum': 1}}},
        {'$sort': {'total': -1}},
        {'$limit': 20}
    ]
    totals = db.interjections.aggregate(pipeline)
    print '\n    TOP INTERJECTORS, HOUSE OF REPRESENTATIVES, 1901-80'
    print '    ==============================================+====\n'
    for total in totals:
        speaker = db.interjections.find_one({'speaker.id': total['_id'], 'speaker.fullname': {'$exists': 1}})
        print '    {:30} {} interjections'.format(speaker['speaker']['fullname'], total['total'])


def list_interjections(text=None, debate=None, house=None, year=None, length=50):
    dbclient = MongoClient(MONGO_URL)
    db = dbclient.get_default_database()
    query = {}
    if text:
        query['$text'] = {'$search': text}
    if debate:
        query['debate'] = debate
    if year:
        query['year'] = year
    if length:
        query['length'] = {'$lte': length}
    if house:
        query['house'] = house
    interjections = db.interjections.find(query).sort('year', 1)
    print '| Interjection | Speaker | Year |'
    print '|----|----|----|'
    for interjection in interjections:
        print '| [{}]({}) | {} | {} |'.format(interjection['text'].encode('utf-8'), interjection['url'], interjection['speaker']['name'], interjection['year'])


def load_portraits():
    dbclient = MongoClient(MONGO_URL)
    db = dbclient.get_default_database()
    originals_dir = os.path.join(IMAGE_DIR, 'originals')
    avatars_dir = os.path.join(IMAGE_DIR, 'avatars')
    images = [i for i in os.listdir(originals_dir) if i[-4:] == '.jpg']
    for image_file in images:
        hansard_id = image_file[:image_file.find('_')]
        print hansard_id
        matches = db.interjections.update_many({'speaker.id': hansard_id}, {'$set': {'speaker.avatar': True}})
        if matches.modified_count > 0:
            im = Image.open(os.path.join(originals_dir, image_file))
            avatar_size = (50, 50)
            avatar = ImageOps.fit(im, avatar_size, Image.ANTIALIAS, centering=(0.5, 0.5))
            avatar_file = '{}.jpg'.format(hansard_id)
            try:
                avatar.save(os.path.join(avatars_dir, avatar_file))
            except IOError:
                avatar = avatar.convert('RGB')
                avatar.save(os.path.join(avatars_dir, avatar_file))


