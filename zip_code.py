#!/bin/env python
import os
import logging
import zipfile
import io
import csv
import urllib
from PIL import Image
import paramiko

def get_zip_path(root_folder, book_id, volume='0'):
    book_id = book_id + '_' + volume.lstrip('0')
    # print book_id

    try:
        for a_file in os.listdir(root_folder):
            disk_folder = os.path.join(root_folder, a_file)
            if 'disk5' in disk_folder:
                disk_folder = os.path.join(disk_folder, 'JP2')
            for b_file in os.listdir(disk_folder):
                if book_id in b_file:
                    # print b_file
                    if int(b_file.split('_')[1]) == int(volume):
                        if 'disk5' in disk_folder:
                            return os.path.join(root_folder, os.path.join(os.path.join(a_file, 'JP2'), b_file))
                        else:
                            return os.path.join(root_folder, os.path.join(a_file, b_file))
    except Exception as e:
        logger.debug('get_zip_path error {} {}'.format(
            str(e),
            type(e))
        )

        print('get_zip_path', str(e), type(e))

        return None




def find_zip(book_id, volume='0'):
    #web_folder = os.path.join('', 'media')
    #web_folder = os.path.join(web_folder, 'page_zips')

    #root_folder = os.path.join(BASE_DIR, 'lost_visions')
    #root_folder = os.path.join(root_folder, 'static')
    #root_folder = os.path.join(root_folder, web_folder)
    ## zip_path = '/home/ubuntu/PycharmProjects/Lost-Visions/lost_visions/static/media/images/003871282_0_1-324pgs__1023322_dat.zip'
    root_folder = os.path.join('/lost-visions','zips')

    zip_path = get_zip_path(root_folder, book_id, volume)

    if zip_path is None:
        return None
    logger.debug('Found %s' % (zip_path))
    archive = None
    try:
        archive = zipfile.ZipFile(zip_path, 'r')
    except:
        logger.error("Problem with %s" % (zip_path))
        return None 
     
    return archive


def find_page(row_id, book_id, page, volume, sftp):

    archive = find_zip(book_id, volume)
    if archive is None:
        logger.debug('archive book id {}, vol {} not found'.format(book_id, volume))

        return None

    inner_zipped_file = None
    for zipped_file in archive.namelist():
        page_number_found = zipped_file.split('_')[-1]
        page_number_found = page_number_found.split('.')[0]
        if int(page) == int(page_number_found):
            inner_zipped_file = zipped_file

    if inner_zipped_file is None:
        logger.debug('could not find page {} in archive'.format(page))
        return None

    # imgdata = archive.read('JP2\\003871282_000015.jp2')
    imgdata = archive.read(inner_zipped_file)

    logger.debug('Read file data from zip'.format(page))

    #input_image = io.StringIO(imgdata)
    input_image = io.BytesIO(imgdata)
    input_image.seek(0)
    img = Image.open(input_image)

    # save as jpeg instead of jpeg2000. Probable loss of quality

    jpgfile = "%s_%s" % (row_id, str(inner_zipped_file).replace('.jp2', '.jpg'))
    logger.debug('Created response for compressed jpeg image')
    logger.debug(jpgfile)
    if sftp:
        with sftp.open(os.path.join('/scratch/c.sistg1/lv_extract_page',
                                    urllib.parse.quote_plus(jpgfile)), 'w') as fp: 
            img.save(fp,"JPEG", quality=80, optimize=True, progressive=True)
    else:    
        img.save(os.path.join('pages',urllib.parse.quote_plus(jpgfile)))

    logger.debug('Saved image')
    return None


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                              '%m-%d-%Y %H:%M:%S')
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

handler = logging.FileHandler('mylog.log')
# create a logging format
handler.setFormatter(formatter)
handler.setLevel(logging.ERROR)
logger.addHandler(handler)

# Set ssh connection

ssh = paramiko.SSHClient()
ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
ssh.connect('xxxx.com', username='xxxx' )
sftp = ssh.open_sftp()

# Test reading CSV
start_id = str(43860)
startfound = True
with open('dataset.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         
         if start_id == row['id']:
             startfound = True
         elif not startfound:
             continue
         find_page(row['id'], row['book_identifier'], row['page'], row['volume'], sftp)

sftp.close()
ssh.close()
