# Carnet-http
Control and automate your Volkswagen through http

## Installing
**Requirements**
* Amazon AWS & developer accounts

Create a new lambda function with the microservice blueprint.<br>
Upload `lambda_function.py` and the  `modules` folder as a .zip file to the new lambda function.<br>
Add your username and password to `lambda_function.py` in the `VWCarnet` constructor.<br>
In the AWS console for your function select the API Gateway trigger and open it.<br>
Go to `ANY` > `Integration Request` and check `Use lambda proxy integration`

## Usage
Using the `Invoke URL` from the lambda function trigger the function takes two GET variables `task` and `action`.<br>
`action` can be either `start` or `stop` while `task` can be `charging`, `heating` & `windowheating`.<br>
Using IFTTT and webhooks you can then start any of these tasks using things such as the weather, calendar events or homescreen widgets.

## Do you own an Echo?
Look no further than [here](https://github.com/Strosel/Carnet-alexa) or the echo version.

## Huge Thank you to
@robinostlund: https://github.com/robinostlund/volkswagen-carnet
