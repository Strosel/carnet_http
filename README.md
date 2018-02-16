# Carnet-http
Control and automate your Volkswagen through http

## Installing
**Requirements**
* Amazon AWS & developer accounts

Create a new lambda function with the microservice blueprint.<br>
Upload `lambda_function.py` and the  `modules` folder as a .zip file to the new lambda function with `lambda_function.main` as the handler and a timeout of 1min 30s or more.<br>
Add your username and password to `lambda_function.py` in the `VWCarnet` constructor.<br>
Go back to the aws console, open API Gateway and create a new API. Give it a name and click "create API".<br>
Click "Actions" and "Create Method" select the "GET" trigger. <br>
In the setup give it "Lambda Function", "Use Lambda Proxy integration", select your region and function and save. <br>
Go back to the Lambda function and give it the "API Gateway" trigger, select the API you just created. Make it "Open". <br>
You should now have a card with information about the trigger, including a link to trigger it. <br>
Save and you're done!

## Usage
Using the `Invoke URL` from the lambda function trigger the function takes two GET variables `task` and `action`.<br>
`action` can be either `start` or `stop` while `task` can be `charging`, `heating` & `windowheating`.<br>
Using IFTTT and webhooks you can then start any of these tasks using things such as the weather, calendar events or homescreen widgets.

## Do you own an Echo?
Look no further than [here](https://github.com/Strosel/Carnet-alexa) or the echo version.

## Huge Thank you to
@robinostlund: https://github.com/robinostlund/volkswagen-carnet
