# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# NECESSARY PACKAGES
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import requests
import itertools as itert
import warnings
import time
import socket
from multiprocessing.dummy import Pool
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# GLOBAL VARIABLES
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
sample_url = "http://7e3dbca9.bwtest-aws.pravala.com/384MB.jar"

current_path = os.getcwd()
destination = current_path + "\\downloads\\"
if not os.path.exists(destination):
	os.makedirs(destination)

unit_size = 1048576
num_chunks = 4
download_size = unit_size * num_chunks
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# FUNCTION DEFINITIONS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def ask_for_url():
	download_url = str(raw_input('Please enter the full url for the file you wish to download:	'))
	if(len(download_url) < 1):
		print 'Invalid url. Sample url will be downloaded instead:'
		print '	' + sample_url
		download_url = sample_url

	return download_url

def filename_from_url(url):
	return url.split('/')[-1]

def get_file_info(url):
	try:
		response = requests.head(url)
		return response.headers
	except Exception as e:
		print e
		print
		print 'Server response header was faulty. Process will terminate unsuccessfully'
		sys.exit(1)

def calculate_file_size(response_header):
	# https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.13
	# "The Content-Length entity-header field indicates the size of the entity-body, in decimal number of OCTETs"
	# An OCTET is 8 bits
	# Here, we assume the popular definition of a byte = 8 bits, even though the definition of byte is system-dependent!
	# 1 MiB = 1024^2 bytes = 1048576 bytes
	try:
		file_size = int(download_url_file_info['Content-Length'])
		return file_size
	except Exception as e:
		print e
		print
		print 'Server response header was faulty. Process will terminate unsuccessfully'
		sys.exit(1)

def download_whole_file(url, save_to):
	start_time = time.clock()
	try:
		response = requests.get(url)
		with open((destination + save_to), 'wb') as test_download_file:
			test_download_file.write(response.content)
		test_download_file.close()
	except Exception as e:
		print e
		print
		print 'Download was unsuccessful'
		sys.exit(1)
	finally:
		end_time = time.clock()
		full_process_time = (end_time - start_time), 'seconds'
		print '	Download attempt was over in ' + str(full_process_time) + ' CPU clocks'


def download_file_partial(url, save_to):
	start_time = time.clock()
	try:
		print 'Only the first 4 MiB of the file will be requested'
		# 4 MiB = 4194000 bytes
		headers = {'Range': ('bytes=0-' + str(download_size))}
		response = requests.get(url, headers = headers)
		with open((destination + save_to), 'wb') as test_download_file:
			test_download_file.write(response.content)
	except Exception as e:
		print e
		print
		print 'Download was unsuccessful'
		sys.exit(1)
	finally:
		end_time = time.clock()
		full_process_time = (end_time - start_time), 'seconds'
		print 'Download attempt was over in ' + str(full_process_time) + ' CPU clocks'

def download_file_chunks(url, save_to, size, chunks):
	start_time = time.clock()
	chunk_size = int(size / chunks)
	current_chunk_pointer = 0
	
	try:
		file_handle = open(destination + save_to, 'wb')
		headers = {'Range': ('bytes=0-' + str(download_size))}
		response = requests.get(url, headers = headers, stream = True)
		for chunk in response.iter_content(chunk_size=chunk_size):
			print chunk
			if chunk:
				file_handle.write(chunk)
				file_handle.flush()
                os.fsync(file_handle.fileno())
	except Exception as e:
		print e
		print
		print 'Download was unsuccessful'
		sys.exit(1)
	finally:
		end_time = time.clock()
		full_process_time = (end_time - start_time), 'seconds'
		print 'Download attempt was over in ' + str(full_process_time) + ' CPU clocks'

def download_file_chunks2(url, save_to, size, chunks):
	start_time = time.clock()
	chunk_size = int(size / chunks)
	current_chunk_pointer = 0
	
	try:
		file_handle = open(destination + save_to, 'wb')
		
		for i in range(1,5,1):
			header_range = 'bytes=' + str(current_chunk_pointer) + '-' + str(current_chunk_pointer + chunk_size)
			headers = {'Range': header_range}
			response = requests.get(url, headers = headers, stream = True)
			print str(i) + ':	' + header_range
			if response.content:
				file_handle.write(response.content)
				current_chunk_pointer += chunk_size
			else:
				raise Exception('Bad response from remote server!')
	except Exception as e:
		print e
		print
		print 'Download was unsuccessful'
		sys.exit(1)
	finally:
		end_time = time.clock()
		full_process_time = (end_time - start_time), 'seconds'
		print 'Download attempt was over in ' + str(full_process_time) + ' CPU clocks'
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main FUNCTION
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
if __name__ == "__main__":
	print 'Process started at ' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
	print
	try:
		download_url = sys.argv[1:][0]
		if(len(download_url) < 1):
			download_url = ask_for_url()
	except IndexError as ie:
		download_url = str(raw_input("Make sure you have entered the full url for the file you wish to download correctly:	"))
		if(len(download_url) < 1):
			download_url = ask_for_url()

	try:
		save_to = sys.argv[1:][1]
		if(len(save_to) < 1):
			save_to = download_url.split('/')[-1]
	except IndexError as ie:
		save_to = filename_from_url(download_url)
	finally:
		save_to = filename_from_url(download_url)

	print 'Getting file information from remote server . . .'
	download_url_file_info = get_file_info(download_url)
	
	if(download_url_file_info['Accept-Ranges']):
		print 'Remote server accepts range header in ' + download_url_file_info['Accept-Ranges']
	else:
		print 'Remote server does not accept range header'
	
	download_url_file_size = calculate_file_size(download_url_file_info)
	
	if(download_url_file_size < download_size):
		print 'File size is ' + str(download_url_file_size) + ' which is less than 4 MiB'
		print 'Download started at ' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
		download_whole_file(download_url, save_to)
	else:
		print 'File size is ' + str(download_url_file_size) + ' which is more than 4 MiB'
		print 'Download started at ' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
		# 3 options
		# download_file_partial(download_url, save_to)
		# download_file_chunks(download_url, save_to, download_size, num_chunks)
		download_file_chunks2(download_url, save_to, download_size, num_chunks)

	print 'Requested file was saved locally as <' + destination + save_to + '>'
	print
	print 'Process ended at ' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))

	sys.exit(0)