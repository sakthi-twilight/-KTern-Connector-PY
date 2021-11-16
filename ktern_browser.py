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


def get_screenshot(driver):
	time.sleep(0.5)
	return driver.get_screenshot_as_base64()


def handle_command(command):

	global no_of_execution

	log = dict()

	command_id = command[ID]
	command_text = command[COMMAND]
	target = command[TARGET]
	targets = command[TARGETS]
	value = command[VALUE]

	log[COMMANDID] = command_id
	

	split = None
	t1 = None
	t2 = None

	if command_text not in COMMAND_MAIN:
		split = target.split('=')
		if len(split) == 2:
			t1 = split[0]
			t2 = split[1]
		elif len(split) == 3:
			t1 = split[0]
			t2 = split[1] + '=' + split[2]
		elif len(split) == 4:
			t1 = split[0]
			t2 = split[1] + '=' + split[2] + '=' + split[3]


		
	try:
		no_of_execution += 1

		log[MESSAGE] = command_text + EMPTY_SPACE + target

		if command_text == COMMAND_OPEN:
			#Open
			driver.get(url)

		elif command_text == COMMAND_SET_WINDOWS_SIZE:
			#Set Winodws Size
			split = target.split('x')
			t1 = split[0]
			t2 = split[1]
			driver.set_window_size(t1, t2)

		elif command_text == COMMAND_TYPE:
			#Command Type
			by = get_by_from_target(target)
			wait.until(EC.visibility_of_element_located((by,t2))).send_keys(Keys.CONTROL,'a')
			wait.until(EC.visibility_of_element_located((by,t2))).send_keys(Keys.BACKSPACE)
			wait.until(EC.visibility_of_element_located((by,t2))).send_keys(value)

		elif command_text == COMMAND_RUN_SCRIPT or command_text == COMMAND_EXECUTE_SCRIPT:
			#Command Run Script or Execute Script
			driver.execute_script(target)

		elif command_text == COMMAND_CLICK or command_text == COMMAND_CLICK_AT:
			#Command Click or Click At
			by = get_by_from_target(target)
			wait.until(EC.element_to_be_clickable((by,t2))).click()

		elif command_text == COMMAND_MOUSE_OVER or command_text == COMMAND_MOUSE_OUT or command_text == COMMAND_MOUSE_MOVE_AT:
			#Command Mouse Over or Mouse Out or Mouse Move At
			by = get_by_from_target(target)
			element = wait.until(EC.visibility_of_element_located((by,t2)))
			actions = ActionChains(driver)
			actions.move_to_element(element).perform()

		elif command_text == COMMAND_MOUSE_DOWN_AT or command_text == COMMAND_MOUSE_DOWN:
			#Command Mouse Down At orMouse Down
			by = get_by_from_target(target)
			element = wait.until(EC.visibility_of_element_located((by,t2)))
			actions = ActionChains(driver)
			actions.move_to_element(element).click_and_hold().perform()

		elif command_text == COMMAND_MOUSE_UP_AT or command_text == COMMAND_MOUSE_UP:
			#Command Mouse Up At or Mouse Up
			by = get_by_from_target(target)
			element = wait.until(EC.visibility_of_element_located((by,t2)))
			actions = ActionChains(driver)
			actions.move_to_element(element).release().perform()

		elif command_text == COMMAND_STORE_TEXT:
			#Command Store Text
			by = get_by_from_target(target)
			vars[value] = wait.until(EC.visibility_of_element_located((by,t2))).text

		elif command_text == COMMAND_STORE:
			#Command Store
			by = get_by_from_target(target)
			vars[target] = value

		elif command_text == COMMAND_SEND_KEYS:
			#Command Send Keys
			by = get_by_from_target(target)
			key = get_keys_from_value(value)
			wait.until(EC.visibility_of_element_located((by,t2))).send_keys(key)

		elif command_text == COMMAND_DOUBLE_CLICK:
			#Command Double Click
			by = get_by_from_target(target)
			element = wait.until(EC.visibility_of_element_located((by,t2)))
			actions = ActionChains(driver)
			actions.double_click(element).perform()

		elif command_text == COMMAND_STORE_TITLE:
			#Command Store Title
			vars[value] = driver.title

		elif command_text == COMMAND_ECHO:
			#Command Echo
			target = regex.findall(r'\{(.*?)\}',target)[0]
			by = get_by_from_target(target)

		elif command_text == COMMAND_ASSERT_TEXT:
			#Command Assert Text
			by = get_by_from_target(target)
			assert wait.until(EC.visibility_of_element_located((by,t2))).text == value

		elif command_text == COMMAND_ASSERT_TITLE:
			#Command Assert Title
			by = get_by_from_target(target)
			assert driver.title == target

		elif command_text == COMMAND_WAIT_FOR_ELEMENT_VISIBLE or command_text == COMMAND_WAIT_FOR_ELEMENT_VISIBLE_SPACE:
			#Command Wait for Element Visible
			
			by = get_by_from_target(target)
			element = wait.until(EC.visibility_of_element_located((by,t2)))

		elif command_text == COMMAND_WAIT_FOR_ELEMENT_PRESENT or command_text == COMMAND_WAIT_FOR_ELEMENT_PRESENT_SPACE:
			#Command Wait for element Present
			by = get_by_from_target(target)
			element = wait.until(EC.presence_of_element_located((by,t2)))

		elif command_text == COMMAND_WAIT_FOR_ELEMENT_EDITABLE or command_text == COMMAND_WAIT_FOR_ELEMENT_EDITABLE_SPACE:
			#Command Wait for Element Editable
			by = get_by_from_target(target)
			element = wait.until(EC.element_to_be_clickable((by,t2)))

		elif command_text == COMMAND_STORE_VALUE:
			#Command Store Value
			by = get_by_from_target(target)
			vars[value] = wait.until(EC.visibility_of_element_located((by,t2))).get_attribute("value")

		elif command_text == COMMAND_ASSERT_VALUE:
			#Command Assert Value
			by = get_by_from_target(target)
			val = wait.until(EC.visibility_of_element_located((by,t2))).get_attribute("value")
			assert val == value

		elif command_text == COMMAND_ASSERT:
			#Command Assert
			by = get_by_from_target(target)
			assert vars[target] == value

		elif command_text == COMMAND_ASSERT_SELECTED_VALUE:
			#Command Assert Selected Value
			by = get_by_from_target(target)
			val = wait.until(EC.visibility_of_element_located((by,t2))).get_attribute("value")
			assert val == value

		elif command_text == COMMAND_ASSERT_SELECTED_LABEL:
			#Command Assert Selected Label
			by = get_by_from_target(target)
			val = wait.until(EC.visibility_of_element_located((by,t2))).get_attribute("label")
			assert val == value

		elif command_text == COMMAND_PAUSE:
			#Command Pause 
			time.sleep(target)

		elif command_text == COMMAND_CLOSE:
			#Command Close 
			driver.close()

		else:
			#Unhandled Command
			no_of_execution = 2
			log[MESSAGE] = COMMAND_NOT_HANDLED
			log[STATUS] = ERROR


		if STATUS not in log: log[STATUS] = SUCCESS 


	except TimeoutException as e:
		#Timeout Exception
		#need to swap the target 

		if no_of_execution < 2:
			command[TARGET] = targets[len(targets) - 1][0]
			log[STATUS] = ERROR
			handle_command(command)
		else:
			log[STATUS] = ERROR
			log[MESSAGE] = str(e)
			no_of_execution = 2

	except Exception as e:
		log[STATUS] = ERROR
		log[MESSAGE] = str(e)
		no_of_execution = 2

	finally:

		if log[STATUS] == SUCCESS or  no_of_execution == 2:
			log[SCREENSHOT] = get_screenshot(driver)
			return log


def exception(e):
	exception = dict()
	exception[EMIT] = ERROR
	exception[MESSAGE] = e
	return exception

def is_valid_browser(browser):
	if browser in VALID_BROWSERS:
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


if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--file', help=FILE_HELP)
	parser.add_argument('--browser', help=BROWSER_HELP)
	parser.add_argument('--user', help=USER_HELP)
	args = parser.parse_args()

	browser = args.browser
	file = args.file
	user = args.user

	logs = []
	vars = {}
	
	if not browser or not file or not is_valid_browser(browser) or not is_file_exists(file):
		print(json.dumps(exception(ARGS_CANNOT_BE_EMPTY)))
		sys.exit()
	

	if browser == FIREFOX:
		driver = webdriver.Firefox(executable_path='./libs/ktern/drivers/geckodriver.exe')
		# driver = webdriver.Firefox(executable_path='./drivers/geckodriver.exe')
	elif browser == CHROME:
		driver = webdriver.Chrome(executable_path='./libs/ktern/drivers/chromedriver.exe')
		# driver = webdriver.Chrome(executable_path='./drivers/chromedriver.exe')
	elif browser == EDGE:
		driver = webdriver.Edge(executable_path='./libs/ktern/drivers/msedgedriver.exe')
		# driver = webdriver.Edge(options=options,executable_path='./drivers/msedgedriver.exe')
	elif browser == EDGE_LEGACY:
		driver = webdriver.Edge()
	elif browser == SAFARI:
		driver = webdriver.Safari()
	elif browser == IE:
		driver = webdriver.Ie(executable_path='./libs/ktern/drivers/IEDriverServer.exe')
		# driver = webdriver.Ie(options=options,executable_path='./drivers/IEDriverServer.exe')
	else:
		driver = webdriver.Chrome(executable_path='./libs/ktern/drivers/chromedriver.exe')

	wait = WebDriverWait(driver, 20)
	data = get_json_from_file(file)

	recording = data[RECORDING][0]
	name = recording[NAME]
	url = recording[URL]
	tests = recording[TESTS][0]
	commands = tests[COMMANDS]


	for command in commands:
		no_of_execution = 0
		log = handle_command(command)
		logs.append(log)

		if log[STATUS] == ERROR: break
	
	logs_result = dict()
	logs_result[PROJECTNAME] = name
	logs_result[LOGS] = logs

	data[LOGS] = logs_result
	data[EMIT] = SAVE_LOG
	data[BROWSER] = browser
	data[USER] = user
	driver.quit()
	print(json.dumps(data))
	sys.exit()
	