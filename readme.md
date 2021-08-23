**********************************
Tools Information
**********************************

- python 3.7
- Install request library using
	python pip install requests==2.26.0
- Created python virtual enviroment and installed all dependencies there
- Used pychram as IDE



**********************************
How to execute test cases
**********************************

1) Install required dependencies using => pip install -r requirements.txt
		- dependencies are  [Flask==2.0.1, psutil==5.8.0, requests==2.26.0]

2) Run service under test using => python3 psweb.py
		- Above service will run at http://localhost:8080/

3) Run test service using => python3 test_psweb.py
		- Above service will run at http://localhost:9090/
		- You can access http://localhost:9090/smoke
		- You can access http://localhost:9090/regression
		
Note:-
Test service is dependent to process service (service under test).

	
**********************************
Idea
**********************************
1) Idea here is to create a service called Test Case as a Service (TaaS)
2) I have created couple of classes and one is <TestConfig> which holds the configurations
3) On same note I have created a class<TestCases> class which contains diffrent resuable test cases
4) For storing the test case output I have created a class <ResultStore>
5) Then we have leverage flask api to exeute our test cases and display the output in json response
5) Definitley this solution will work on any platform


*******************************
Disclaimer
*******************************

1) I have spent 3 hours in this exercise and I know its not a complete solution/framework, in short there is alot more
2) I can come up with infinite testcases and scenarios but condidering time I have choosed scenerios with max coverage
3) Right now I have wrote all of my code in single file (test_psweb.py) but in reality this will not be case
4) I did commenting in the code to give an idea on my approach
