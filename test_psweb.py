###################################
# Requirements
###################################
# python 3.7
# Install request library using => python pip install requests==2.26.0


####################################
# How to execute test cases
####################################
# 1) Install required dependencies using => pip install -r requirements.txt
#       => dependencies are  [Flask==2.0.1, psutil==5.8.0, requests==2.26.0]
#
# 2) Run service under test using => python3 psweb.py
#       => Above service will run at http://localhost:8080/
#
# 3) Run test service using => python3 test_psweb.py
#       => Above service will run at http://localhost:9090/
#       => You can access http://localhost:9090/smoke
#       => You can access http://localhost:9090/regression


####################################
# Disclaimer
#####################################
# I have spent 3 hours in this exercise. This is not a finished product and is only for to give an idea.
# I know we can do a lot more
#####################################


import requests
from flask import Flask, jsonify, abort


# Below is the base class or you can say config class
# Right now I am just declaring a variable but in reality it should be reading a configuration file (.yml,xml, json)
class TestConfig(object):
    baseUrl = "http://localhost:8080"


# Below class contains reusable test cases and its derived from TestConfig class
# I haven't did the exception handling in this class because I did it where I will call these methods
class TestCases(TestConfig):
    # Below method is a test case which is responsible for verifying response code
    # Its takes 3 parameters. method name, endpoint and dictionary of parameters
    # p stand for parameter, str stands for string and dict stands for dictionary
    def tc_verify_reposne_end_point(self, pstr_method, pstr_end_point, pdict_para):
        if (pstr_method in ['GET', 'POST']):
            url = self.baseUrl + pstr_end_point
            response = requests.request(method=pstr_method, url=url, params=pdict_para)
            response_code = response.status_code
            if (response_code == 200):
                return True
            else:
                return False
        else:
            # Idea is to log information here if some thing goes wrong
            return False

    # Below method is a test case which is used to verify the value of maximum memory and threads above
    # We will extract the value form process service and compare it with given values
    # It takes 2 parameters. 1st is memory above value and 2nd is process above number
    def tc_verify_mem_thread_above(self, pint_mem_above, pint_process_above):
        url = self.baseUrl + "/processes?mem-above=" + str(pint_mem_above) + "&threads-above=" + str(pint_process_above)
        response = requests.get(url=url)
        if (response.status_code == 200):
            json = response.json()
            for process in json:
                mem_per = json[process]["memory_percent"]
                num_threads = json[process]["num_threads"]
                if (float(mem_per) < pint_mem_above or int(num_threads) < pint_process_above):
                    return False
            return True
        else:
            # Idea is to log information here if some thing goes wrong
            return False

    # This test case verify the attributes of the endpoint in returned json
    # parameter <pdict_para> holds dict of parameters
    # parameter <plst_attr> holds list of attributes
    def tc_verify_schema_attribute(self, pstr_method, end_point, pdict_para, plst_attr):
        url = self.baseUrl + end_point
        response = requests.request(method=pstr_method, url=url, params=pdict_para)
        json = response.json()
        if len(json):
            for item in json:
                item_value = json[item]
                lst_attr = list(item_value.keys())
                if (lst_attr != plst_attr):
                    return False
            return True
        else:
            return True


# Below class is responsible for storing test results in variable <tc_json_result> list of dict
# Our idea is to store the test cases output in json format so that we can show it on response
class ResultStore:
    # Below variable is acting as static member to store dicts
    tc_json_result = list()

    # Below method takes two parameters test case name and test case status (True or false)
    # Creates a dict and stores it to above list
    def add_result_to_list(self, pstr_tc_name, pstr_tc_status):
        _dict = dict()
        _dict['test_case_name'] = pstr_tc_name
        _dict['test_case_status'] = pstr_tc_status
        self.tc_json_result.append(_dict)

    # To get the list or you can say variable <tc_json_result>
    def get_tc_results(self):
        return self.tc_json_result

    # If we want to clear the list then we will call this method
    # As this list will store all of test case results
    def clear_tc_results(self):
        self.tc_json_result.clear()




######################################################
# Below is the rest api code using flask
# I am using flask as test cases runner like we have pytest
######################################################

app = Flask(__name__)


# This is kind to index page
@app.route('/')
def index():
    return '''
        <h1>Test Case as a Service</h1>
        <p>To run smoke test cases : <a href="/smoke">/smoke</a> </p>
        <p>To run regression test cases: <a href="/regression">/regression</a> </p>
    '''


# This endpoint will call all of the smoke testcases
@app.route('/smoke')
def smoke():
    try:
        test_cases = TestCases()
        store_result = ResultStore()
        # Samples is a list of different variations of test inputs
        # And these inputs are supplied to test cases, kind of variations for maximum coverage
        # We can supply as many inputs as we want
        samples = [
            {
                'method': 'GET',
                'endpoint': '/processes',
                'query_parameter': {}
            },
            {
                'method': 'GET',
                'endpoint': '/processes/0',
                'query_parameter': {}
            },
            {
                'method': 'GET',
                'endpoint': '/processes',
                'query_parameter': {'mem-above': '1', 'threads-above': '1'}
            },
            {
                'method': 'GET',
                'endpoint': '/processes',
                'query_parameter': {'mem-above': '1'}
            }
        ]

        store_result.clear_tc_results()

        for samp in samples:
            _method = samp['method']
            _endpoint = samp['endpoint']
            _dict_params = samp['query_parameter']
            # Calling the test case with different inputs and getting result (true/false)
            res = test_cases.tc_verify_reposne_end_point(pstr_method=_method, pstr_end_point=_endpoint,
                                                         pdict_para=_dict_params)
            # Storing the result and testcase name in the ResultStore
            store_result.add_result_to_list(
                    pstr_tc_name="verfiy the status of endpoint <" + _endpoint + "> is 200 with parameters " +
                             str(_dict_params)
                   , pstr_tc_status=res)

        response = jsonify(store_result.get_tc_results())
        return response
    except Exception as e:
        abort(404)


# If we wanna call all regression test cases then we will call this endpoint
@app.route('/regression')
def regression():
    try:
        # Calling the smoke test cases here as defined in above function
        # Because in regression we try to execute maximum test cases
        smoke()

        test_cases = TestCases()
        store_result = ResultStore()

        samples = [
            {'mem_above': 6.1, 'process_above': 3},
            {'mem_above': 7.1, 'process_above': 4}
        ]

        for samp in samples:
            mem_above = samp['mem_above']
            process_above = samp['process_above']
            # Calling the test cases for verifying <memory_percent/num_threads> values in response
            res = test_cases.tc_verify_mem_thread_above(pint_mem_above=mem_above, pint_process_above=process_above)
            store_result.add_result_to_list(
                pstr_tc_name="verify with mem-above = " + str(mem_above) + " and threads-above = " + str(process_above)
                             + ", the value of <memory_percent> and <num_threads> in response"
                , pstr_tc_status=res
            )

        # Samples are inputs to testcase as variation for maximum coverage
        samples = [
            {
                'method': 'GET',
                'endpoint': '/processes',
                'query_parameter': {'mem-above': '1', 'threads-above': '1'},
                'attributes': ['memory_percent', 'name', 'num_threads', 'pid']
            },
            {
                'method': 'GET',
                'endpoint': '/processes',
                'query_parameter': {'mem-above': '5'},
                'attributes': ['memory_percent', 'name', 'num_threads', 'pid']
            },
            {
                'method': 'GET',
                'endpoint': '/processes',
                'query_parameter': {},
                'attributes': ['memory_percent', 'name', 'num_threads', 'pid']
            },
        ]

        for samp in samples:
            _method = samp['method']
            _endpoint = samp['endpoint']
            _dict_parameters = samp['query_parameter']
            _lst_attr = samp['attributes']
            # Calling verify schema test case here
            res = test_cases.tc_verify_schema_attribute(pstr_method=_method
                                                        , end_point=_endpoint
                                                        , pdict_para=_dict_parameters
                                                        , plst_attr=_lst_attr)
            lst_to_str = ", ".join(_lst_attr)
            store_result.add_result_to_list(
                pstr_tc_name="verify valid attributes [" + lst_to_str + "] for endpoint <" + _endpoint + ">"
                , pstr_tc_status=res)

        response = jsonify(store_result.get_tc_results())
        return response
    except Exception as e:
        abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
