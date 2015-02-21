# box-demo
Box integration webapp

### Requirements
- python 2.7
- virtualenvwrapper
- node.js

### Set-up development enviroment
```sh
# get the code
git clone https://github.com/enikesha/box-demo
# start python virtualenv
mkvirtualenv box-demo
cd box-demo
# Install python requirements
pip install -r requirements.txt
# Install node.js requirements
npm install
# Install bower dependencies
bower install
# Init database
./manage.py migrate
# Build static files
gulp build
```
