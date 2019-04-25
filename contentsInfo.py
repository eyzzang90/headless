# -*- coding: utf-8 -*-

import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import datetime
import sys
sys.path.append('/settings')
from settings import config


def performance(driver):
	performance_log = driver.get_log('performance')
	return performance_log


def get_network_response(log):

	response_list = get_network_info(log, 'Network.responseReceived')
	loading_finished_list = get_network_info(log, 'Network.loadingFinished')

	network_response = []

	for response in response_list:
		resp = response['response']
		req_id = response['requestId']
		
		for finished in loading_finished_list:
			fin_req_id = finished['requestId']
			fin_time_stamp = finished['timestamp']*1000

			if fin_req_id == req_id:

				print('=========================================================================================================')
				print('requestId: ', req_id)

				status = resp['status']
				print('status: ', status)

				url = resp['url']
				print('url: ', url)

				# print('headers', resp['headers'])
				content_type = resp['headers'].get('content-type') if resp['headers'].get('content-type') is not None else resp['headers'].get('Content-Type')
				print('Content-Type: ', content_type)
			
				content_length = resp['headers'].get('content-length') if resp['headers'].get('content-length') is not None else resp['headers'].get('Content-Length')
				content_length = str(finished['encodedDataLength'])+'B' if content_length is None else str(round(int(content_length)))+'B'

				# print('timing', resp['timing'])
				# respTime = (resp['timing']['receiveHeadersEnd'] - resp['timing']['sendEnd'])
				# print('wait time: {0}{1}'.format(round(respTime, 1), 'ms'))

				'''
				totalTime 구하기 참고자료
				https://source.ind.ie/forks/chrome-har-capture/
				'''

				dns_time = timing_delta(resp['timing']['dnsStart'], resp['timing']['dnsEnd'])
				# print('dnsTime: ', dns_time)

				connect_time = timing_delta(resp['timing']['connectStart'], resp['timing']['connectEnd'])
				# print('connectTime: ', connect_time)

				# proxy_time = timing_delta(resp['timing']['proxyStart'], resp['timing']['proxyEnd'])
				# print('proxyTime: ', proxy_time)

				send_time = timing_delta(resp['timing']['sendStart'], resp['timing']['sendEnd'])
				# print('sendTime: ', send_time)

				ssl_time = timing_delta(resp['timing']['sslStart'], resp['timing']['sslEnd'])
				# print('sslTime: ', ssl_time)

				wait_time = resp['timing']['receiveHeadersEnd'] - resp['timing']['sendEnd']
				# print('waitTime: ' , wait_time)

				receive_time = fin_time_stamp - (resp['timing']['requestTime']*1000 + resp['timing']['receiveHeadersEnd'])
				print('finTimeStamp: ', fin_time_stamp)
				print('requestTime: ', resp['timing']['requestTime']*1000)

				total_time = dns_time + connect_time + send_time + wait_time + receive_time + ssl_time
				print('totalTime: {0}{1}'.format(round(total_time, 1), 'ms'))
				print('=========================================================================================================')

				data_dic = dict()

				data_dic['url'] = url
				data_dic['status'] = status
				data_dic['contentType'] = content_type
				data_dic['size'] = content_length
				data_dic['time'] = str(round(total_time))+'ms'

				network_response.append(data_dic)

	return network_response


def get_network_responses(log):

	response_list = get_network_info(log, 'Network.responseReceived')
	loading_finished_list = get_network_info(log, 'Network.loadingFinished')
	# dom_content_event_fired = get_network_info(log, 'Page.domContentEventFired')
	# frame_navigated = get_network_info(log, 'Page.frameNavigated')
	# frame_stopped_loading = get_network_info(log, 'Page.frameStoppedLoading')
	# load_event_fired = get_network_info(log, 'Page.loadEventFired')
	# data_received = get_network_info(log, 'Network.dataReceived')
	# loading_failed = get_network_info(log, 'Network.loadingFailed')
	# request_will_be_sent = get_network_info(log, 'Network.requestWillBeSent')
	# request_served_from_cache = get_network_info(log, 'Network.requestServedFromCache')
	# resource_changed_priority = get_network_info(log, 'Network.resourceChangedPriority')

	total_response = {}
	network_response = []

	total_size = 0
	total_requests = 0
	# total_time = 0

	for response in response_list:
		resp = response['response']
		req_id = response['requestId']

		for finished in loading_finished_list:
			fin_req_id = finished['requestId']
			fin_time_stamp = finished['timestamp']*1000
			if fin_req_id == req_id:

				url = resp['url']
				status = resp['status']
				content_type = resp['headers'].get('content-type') if resp['headers'].get('content-type') is not None else resp['headers'].get('Content-Type')
				encoded_data_length = finished['encodedDataLength']

				# content_length = resp['headers'].get('content-length')
				# Content_Length = resp['headers'].get('Content-Length')

				dns_time = timing_delta(resp['timing']['dnsStart'], resp['timing']['dnsEnd'])
				connect_time = timing_delta(resp['timing']['connectStart'], resp['timing']['connectEnd'])
				# proxy_time = timing_delta(resp['timing']['proxyStart'], resp['timing']['proxyEnd'])
				send_time = timing_delta(resp['timing']['sendStart'], resp['timing']['sendEnd'])
				ssl_time = timing_delta(resp['timing']['sslStart'], resp['timing']['sslEnd'])
				wait_time = resp['timing']['receiveHeadersEnd'] - resp['timing']['sendEnd']
				receive_time = fin_time_stamp - (resp['timing']['requestTime']*1000 + resp['timing']['receiveHeadersEnd'])
				total_time = dns_time + connect_time + send_time + wait_time + receive_time + ssl_time
				
				total_size += encoded_data_length
				total_requests += 1

				data_dic = dict()

				data_dic['url'] = url
				data_dic['status'] = status
				data_dic['contentType'] = content_type
				data_dic['size'] = str(encoded_data_length)+'B'
				data_dic['time'] = str(round(total_time))+'ms'

				network_response.append(data_dic)

	total_response['totalSize'] = total_size
	total_response['totalRequests'] = total_requests
	total_response['networkResponse'] = network_response

	return total_response


'''
	type 종류
	Page.domContentEventFired	활용도 X
	Page.frameNavigated			페이지 내 iframe으로 호출하는 값들의 정보
	Page.frameStoppedLoading	활용도 X
	Page.loadEventFired			활용도 X

	Network.dataReceived
	Network.loadingFinished
	Network.loadingFailed
	Network.requestWillBeSent	간단히 호출할 request정보 담겨있음.
	Network.requestServedFromCache
	Network.responseReceived
	Network.resourceChangedPriority
'''


def get_network_info(log, type):

	network_info = []
	for entry in log:
		message_str = entry['message']
		message = json.loads(message_str)
		if message['message']['method'] == type:
			# print(entry)
			value = message['message']['params']
			# print(value)
			network_info.append(value)

	return network_info


def timing_delta(start, end):

	return (end-start) if start != 1 and end != -1 else 0


def get_network_performance(url, driver, log):

	network_performance = dict()

	total_response = get_network_responses(log)
	total_size = total_response['totalSize']
	total_requests = total_response['totalRequests']
	# network_response = total_response['networkResponse']
	network_response = []
	total_img_size = 0

	# using navigation timing APIs
	navigation_start = driver.execute_script('return window.performance.timing.navigationStart')
	# 브라우저가 서버나 캐시 혹은 로컬 리소스로부터 처음 byte 응답을 받은 시점
	# response_start = driver.execute_script('return window.performance.timing.responseStart')
	dom_loading = driver.execute_script('return window.performance.timing.domLoading')
	dom_complete = driver.execute_script('return window.performance.timing.domComplete')
	load_event_start = driver.execute_script('return window.performance.timing.loadEventStart')
	load_event_end = driver.execute_script('return window.performance.timing.loadEventEnd')
	# request_start = driver.execute_script('return window.performance.timing.requestStart')
	# response_end = driver.execute_script('return window.performance.timing.responseEnd')
	# dom_content_loaded_event_start = driver.execute_script('return window.performance.timing.domContentLoadedEventStart')
	dom_content_loaded_event_end = driver.execute_script('return window.performance.timing.domContentLoadedEventEnd')

	processing = dom_complete - dom_loading
	page_load_time = load_event_end - navigation_start		# 페이지 로드시간
	load_event = load_event_end - load_event_start		# 브라우저가 window.load 이벤트를 기다리는 자바스크립트 코드를 실행하는데 걸리는 시간
	# 요청 응답시간 (전송/페이지 다운로드 시간)
	# connect_time = response_end - request_start
	# backend_performance = response_start - navigation_start		# 총 첫번째 바이트 시간
	# frontend_performance = dom_complete - response_start
	dom_content_loaded = dom_content_loaded_event_end - navigation_start		# DOM 내용로드 시간

	# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	# print('backendPerformance: %s' % backend_performance)
	# print('frontendPerformance: %s' % frontend_performance)
	# print('pageLoadTime: %s' % page_load_time)
	# print('connectTime: %s' % connect_time)
	# print('loadEvent: %s' % load_event)
	# print('processing: ', processing)
	# print('domContentLoaded: ', dom_content_loaded)
	# print('onLoad: ', load_event + processing)
	# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

	img_size = int(config.img_size)

	for response in total_response['networkResponse']:

		# 30K 이상 이미지들에 대해서 size 저장
		res_size = response['size']
		int_size = int(res_size[:-1])
		content_type = response['contentType']

		if int_size >= img_size and 'image' in content_type:
			network_response.append(response)

		# image file 에 대해서만 따로 size 체크. totalSize 구한다.
		if content_type is not None and 'image' in content_type:
			total_img_size += int_size

	# transfer scroll height
	last_height = driver.execute_script('return document.body.scrollHeight')

	while True:

		# scroll down to bottom
		driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

		# get network response
		logs = driver.get_log('performance')
		total_response2 = get_network_responses(logs)
		total_size += total_response2['totalSize']
		total_requests += total_response2['totalRequests']
		# imgSize =

		for response in total_response2['networkResponse']:

			# 30K 이상 이미지들에 대해서 size 저장
			res_size = response['size']
			int_size = int(res_size[:-1])
			content_type = response['contentType']

			if int_size >= img_size and 'image' in content_type:
				network_response.append(response)
				print('더한다')

			# image file 에 대해서만 따로 size 체크. totalSize 구한다.
			if content_type is not None and 'image' in content_type:
				total_img_size += int_size

		# wait to load page
		time.sleep(5)

		new_height = driver.execute_script('return document.body.scrollHeight')		# 문서 세로길이

		if new_height == last_height:
			break
		else:
			last_height = new_height
	print('Reached to the bottom of the page! ')
	print('totalSize', total_size)
	print('totalRequests', total_requests)
	print('totalImgSize', total_img_size)

	network_performance['url'] = url
	network_performance['totalSize'] = str(round(int(total_size)/(1024*1024), 1))+'MB'
	network_performance['imgSize'] = str(round(int(total_img_size)/(1024*1024), 1))+'MB'
	network_performance['requests'] = total_requests
	network_performance['onLoad'] = str(round((load_event + processing)/1000, 1))+'s'
	network_performance['domContentLoaded'] = str(round(dom_content_loaded/1000, 1))+'s'
	network_performance['pageLoadTime'] = str(round(page_load_time/1000, 1))+'s'

	network_response = sorted(network_response, key=lambda d: int(d['size'][:-1]), reverse=True)
	network_performance['networkResponse'] = network_response

	current_time = datetime.datetime.today().strftime('%Y%m%d%H%M%S')

	network_performance['currentTime'] = current_time

	# network_performance['lastHeight'] = lastHeight

	return network_performance


def get_content_url(search_url_str, response_list):

	content_url = None

	for response in response_list:
		resp = response['response']

		url = resp['url']
		idx = url.find(search_url_str)
		if idx != -1:
			content_url = url

	return content_url
