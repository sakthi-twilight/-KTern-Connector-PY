import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import argparse
from browser_constants import *
import os
import regex
import time
import sys

def exception(e):
	exception = dict()
	exception[EMIT] = ERROR
	exception[MESSAGE] = e
	return exception

def is_valid_browser(browser):
	if browser == CHROME or browser == FIREFOX or browser == EDGE or browser == SAFARI or browser == IE or browser == EDGE_LEGACY:
		return True
	return False

def is_file_exists(file):
	if os.path.exists(file):
		return True
	return False

def get_json_from_file(file=DEFAULT_FILE):
	f = open(file)
	json_data = json.load(f)
	f.close()
	return json_data


def get_log_message(command,target):
	return TRYING_TO + command + EMPTY_SPACE + target 

def swap_target():
	global targets,target
	if targets:
		first_target = targets[0][0]
		last_target = targets[len(targets) - 1][0]
		if target == first_target:
			target = last_target
		else:
			target = first_target


def get_by_from_target(t):
	if t.startswith('name='):
		return By.NAME
	elif t.startswith('id='):
		return By.ID
	elif t.startswith('linkText='):
		return By.LINK_TEXT
	elif t.startswith('css='):
		return By.CSS_SELECTOR 
	elif t.startswith('xpath='):
		return By.XPATH

def get_keys_from_value(value):
	value = regex.findall(r'\{(.*?)\}',value)[0]
	if value == ENTER_KEY:
		return Keys.ENTER


def handle_open():

	global is_executed, target,is_first_executed,exception_happened,command_text,url
	
	log = dict()
	log[COMMANDID] = command_id
	
	try:
		log[MESSAGE] = get_log_message(command_text,url)
		driver.get(url)
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		exception_happened = True
	finally:
		logs.append(log)


def handle_setWindowSize():
	
	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id
	try:
		#Spliting the Target
		split = target.split('x')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		driver.set_window_size(t1, t2)
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		exception_happened = True
	finally:
		logs.append(log)


def handle_type():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]

		message_target = ON + target + EMPTY_SPACE + WITH_VALUE + value
		log[MESSAGE] = get_log_message(command_text,message_target)

		by = get_by_from_target(target)
		wait.until(EC.visibility_of_element_located((by,t2))).send_keys(value)
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()
		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
	
	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_type()
			else:
				exception_happened = True


def handle_runScript():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:

		log[MESSAGE] = get_log_message(command_text,target)

		driver.execute_script(target)
		
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_runScript()
			else:
				exception_happened = True


def handle_executeScript():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:

		log[MESSAGE] = get_log_message(command_text,target)

		driver.execute_script(target)
		
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_executeScript()
			else:
				exception_happened = True

def handle_click():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)

		wait.until(EC.element_to_be_clickable((by,t2))).click()
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
	except TimeoutException as e:
		
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True
		
	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_click()
			else:
				exception_happened = True


def handle_mouseOver():
	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)
		
		element = wait.until(EC.visibility_of_element_located((by,t2)))
		actions = ActionChains(driver)
		actions.move_to_element(element).perform()
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()
		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_mouseOver()
			else:
				exception_happened = True

def handle_mouseOut():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)

		by = get_by_from_target(target)
		element = wait.until(EC.visibility_of_element_located((by,t2)))
		actions = ActionChains(driver)
		actions.move_to_element(element).perform()
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_mouseOut()
			else:
				exception_happened = True


def handle_mouseDownAt():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)

		by = get_by_from_target(target)
		element = wait.until(EC.visibility_of_element_located((by,t2)))
		actions = ActionChains(driver)
		actions.move_to_element(element).click_and_hold().perform()
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_mouseDownAt()
			else:
				exception_happened = True



def handle_mouseUpAt():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)

		by = get_by_from_target(target)
		element = wait.until(EC.visibility_of_element_located((by,t2)))
		actions = ActionChains(driver)
		actions.move_to_element(element).release().perform()
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_mouseUpAt()
			else:
				exception_happened = True


def handle_storeText():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)
		vars[value] = wait.until(EC.visibility_of_element_located((by,t2))).text

		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_storeText()
			else:
				exception_happened = True


def handle_store():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)
		vars[target] = value

		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_store()
			else:
				exception_happened = True

def handle_sendKeys():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)

		key = get_keys_from_value(value)

		wait.until(EC.visibility_of_element_located((by,t2))).send_keys(key)


		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_sendKeys()
			else:
				exception_happened = True


def handle_doubleClick():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)

		element = wait.until(EC.visibility_of_element_located((by,t2)))
		actions = ActionChains(driver)
		actions.double_click(element).perform()

		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_doubleClick()
			else:
				exception_happened = True

def handle_storeTitle():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:

		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)
		
		vars[value] = driver.title
		
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_storeTitle()
			else:
				exception_happened = True


def handle_echo():
	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		
		log[MESSAGE] = get_log_message(command_text,target)
		target = regex.findall(r'\{(.*?)\}',target)[0]
		by = get_by_from_target(target)

		# print(str(vars[target]))
		
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_echo()
			else:
				exception_happened = True

def handle_assertText():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)


		assert wait.until(EC.visibility_of_element_located((by,t2))).text == value

		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_assertText()
			else:
				exception_happened = True

def handle_assertTitle():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
	
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)

		assert driver.title == target
		
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_assertTitle()
			else:
				exception_happened = True

def handle_waitForElementVisible():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)

		by = get_by_from_target(target)
		element = wait.until(EC.visibility_of_element_located((by,t2)))

		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()
		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_waitForElementVisible()
			else:
				exception_happened = True

def handle_waitForElementPresent():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)

		by = get_by_from_target(target)
		element = wait.until(EC.presence_of_element_located((by,t2)))
		
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()
		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_waitForElementPresent()
			else:
				exception_happened = True

def handle_waitForElementEditable():
	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)

		by = get_by_from_target(target)
		element = wait.until(EC.element_to_be_clickable((by,t2)))
		
		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()
		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_waitForElementEditable()
			else:
				exception_happened = True

def handle_storeValue():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)
		vars[value] = wait.until(EC.visibility_of_element_located((by,t2))).get_attribute("value")

		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_storeValue()
			else:
				exception_happened = True


def handle_assertValue():

	global is_executed,target,is_first_executed,exception_happened,command_text,value

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)


		val = wait.until(EC.visibility_of_element_located((by,t2))).get_attribute("value")
		assert val == value


		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_assertValue()
			else:
				exception_happened = True

def handle_assertSelectedValue():

	global is_executed,target,is_first_executed,exception_happened,command_text,value

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)


		val = wait.until(EC.visibility_of_element_located((by,t2))).get_attribute("value")
		assert val == value


		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_assertSelectedValue()
			else:
				exception_happened = True

def handle_assertSelectedLabel():

	global is_executed,target,is_first_executed,exception_happened,command_text,value

	log = dict()
	log[COMMANDID] = command_id

	try:
		split = target.split('=')
		t1 = split[0]
		t2 = split[1]
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)


		val = wait.until(EC.visibility_of_element_located((by,t2))).get_attribute("label")
		assert val == value


		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_assertSelectedLabel()
			else:
				exception_happened = True

def handle_assert():

	global is_executed,target,is_first_executed,exception_happened,command_text,value

	log = dict()
	log[COMMANDID] = command_id

	try:
		
		log[MESSAGE] = get_log_message(command_text,target)
		by = get_by_from_target(target)


		assert vars[target] == value


		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_assert()
			else:
				exception_happened = True

def handle_pause():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:

		log[MESSAGE] = get_log_message(command_text,target)

		time.sleep(target)

		is_executed = True
		log[STATUS] = SUCCESS
		log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_pause()
			else:
				exception_happened = True

# def handle_storeWindowHandle():
# 	pass

# def handle_selectWindow():
# 	pass

def handle_close():

	global is_executed,target,is_first_executed,exception_happened,command_text

	log = dict()
	log[COMMANDID] = command_id

	try:

		log[MESSAGE] = get_log_message(command_text,target)

		driver.close()

		is_executed = True
		log[STATUS] = SUCCESS
		# log[SCREENSHOT] = driver.get_screenshot_as_base64()
		
	except TimeoutException as e:
		#Check if the target is first or last
		swap_target()

		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		log[SCREENSHOT] = driver.get_screenshot_as_base64()

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = e.message
		
		is_executed = True
		exception_happened = True

	finally:
		logs.append(log)

		if not is_executed:
			if not is_first_executed:
				is_first_executed = True
				handle_close()
			else:
				exception_happened = True


def handle_default():
	global exception_happened,command_text
	log = dict()
	log[COMMANDID] = command_id
	log[MESSAGE] = command_text + ' is not handled'
	exception_happened = True


if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('--file', help=FILE_HELP)
	parser.add_argument('--browser', help=BROWSER_HELP)
	parser.add_argument('--user', help=USER_HELP)
	args = parser.parse_args()

	exception_happened = False
	is_first_executed = False
	is_executed = False

	browser = args.browser
	file = args.file
	user = args.user

	vars = {}

	logs = []

	if not browser or not file or not is_valid_browser(browser) or not is_file_exists(file):
		print(json.dumps(exception(ARGS_CANNOT_BE_EMPTY)))
		sys.exit()

	if browser == FIREFOX:
		# driver = webdriver.Firefox(executable_path='./libs/ktern/drivers/geckodriver.exe')
		driver = webdriver.Firefox(executable_path='./drivers/geckodriver.exe')
	elif browser == CHROME:
		driver = webdriver.Chrome(executable_path='./libs/ktern/drivers/chromedriver.exe')
		# driver = webdriver.Chrome(executable_path='./drivers/chromedriver.exe')
	elif browser == EDGE:
		driver = webdriver.Edge(executable_path='./libs/ktern/drivers/msedgedriver.exe')
		# driver = webdriver.Edge(executable_path='./drivers/msedgedriver.exe')
	elif browser == EDGE_LEGACY:
		driver = webdriver.Edge()
		# driver = webdriver.Edge(executable_path='./drivers/MicrosoftWebDriver.exe')
	elif browser == SAFARI:
		driver = webdriver.Safari()
	elif browser == IE:
		driver = webdriver.Ie(executable_path='./libs/ktern/drivers/IEDriverServer.exe')
		# driver = webdriver.Ie(executable_path='./drivers/IEDriverServer.exe')
	else:
		driver = webdriver.Chrome(executable_path='./libs/ktern/drivers/chromedriver.exe')
		# driver = webdriver.Chrome(executable_path='./drivers/chromedriver.exe')
	


	wait = WebDriverWait(driver, 15)

	data = get_json_from_file(file)

	recording = data[RECORDING][0]
	# recording = data
	name = recording[NAME]
	url = recording[URL]
	tests = recording[TESTS][0]
	commands = tests[COMMANDS]

	for command in commands:
		
		if exception_happened: 
			break

		is_first_executed = False
		is_executed = False


		command_id = command[ID]
		command_text = command[COMMAND]
		target = command[TARGET]
		targets = command[TARGETS]
		value = command[VALUE]

		{
			'open': handle_open,
			'setWindowSize': handle_setWindowSize,
			'type': handle_type,
			'runScript': handle_runScript,
			'executeScript': handle_executeScript,
			'click': handle_click,
			'clickAt': handle_click,
			'mouseOver': handle_mouseOver,
			'mouseOut': handle_mouseOut,
			'mouseDownAt': handle_mouseDownAt,
			'mouseUpAt': handle_mouseUpAt,
			'mouseDown': handle_mouseDownAt,
			'mouseUp': handle_mouseUpAt,
			'mouseMoveAt':handle_mouseOver,
			'storeText': handle_storeText,
			'store': handle_store,
			'sendKeys': handle_sendKeys,
			'doubleClick': handle_doubleClick,
			'storeTitle': handle_storeTitle,
			'echo': handle_echo,
			'assertText': handle_assertText,
			'assertTitle': handle_assertTitle,
			'waitForElementVisible': handle_waitForElementVisible,
			'waitForElementPresent': handle_waitForElementPresent,
			'waitForElementEditable': handle_waitForElementEditable,
			'storeValue': handle_storeValue,
			'assertValue': handle_assertValue,
			'assert': handle_assert,
			'assertSelectedValue': handle_assertSelectedValue,
			'assertSelectedLabel': handle_assertSelectedLabel,
			'pause': handle_pause,
			'close': handle_close

		}.get(command_text,handle_default)()

	
	logs_result = dict()

	logs_result[PROJECTNAME] = name
	
	logs_result[LOGS] = logs

	data[LOGS] = logs_result
	data[EMIT] = SAVE_LOG
	data[BROWSER] = browser
	data[USER] = user

	driver.quit()

	# print(json.dumps(data))
	sys.exit()


