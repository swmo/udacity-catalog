# udacity-catalog

This project was created for the fullstack Udacity course.
Project: Build an Item Catalog Application

## Getting started

* the easiest way is to start the vagrant maschine (its based on the provided vm from udacity).
  * ```vagrant up```
  * cd /vagrant/
  * start the application ```
python app.py```

  *  open http://localhost:8000

* an other way is to use the default fullstack nanodegree vm and install following packages:
```
sudo pip install flask_wtf
sudo pip install flask_bcrypt
sudo pip install python-resize-image
```
  * cd to /vagrant/catalog/
  * create database: ```python models.py```
  * import the demo data: ```python demodata.py```
  * Start Application with ```python app.py```
  * open http://localhost:8000



