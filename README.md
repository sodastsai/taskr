# Taskr

## Installation

via pip:

```sh
pip install taskr
```



## Usage - Task


### ```@task``` decorator

Setup a task function like (Let's call it as "utils.py" and assume utils.py has execute permission.)

```python
from taskr import task

@task
def run(source, destination, speed=42):
    print('Run from {} to {} by speed={}'.format(source, destination, speed))
   
if __name__ == '__main__':
    task.dispatch()
```

Then execute by

```sh
python utils.py run Tokyo Yokohama
```

or 

```sh
./utils.py run Tokyo Yokohama
```

And you'll get

```
Run from Tokyo to Yokohama by speed=42
```

To get help of utils.py

```sh
$ python utils.py run -h
usage: utils.py run [-h] [--speed SPEED] source destination

positional arguments:
  source
  destination

optional arguments:
  -h, --help     show this help message and exit
  --speed SPEED
```


### ```@task.set_name``` decorator

By default, we make the name of the function as its action/task name.
If you want to change the action name, you can use ```@task.set_name``` decorator like this

```python
@task
@task.set_name('run_to')
def run(source, destination, speed=42):
    print('Run from {0} to {1} by speed={2}'.format(source, destination, speed))
```

And now execute by

```sh
python utils.py run_to Tokyo Yokohama
```


### ```@task.set_argument``` decorator

taskr uses [```argparse```](https://docs.python.org/3/library/argparse.html) module of Python to
parse argument passed in.
By default, we map positional argument of task function into required positonal argument of argparser and
optional argument of task function into optional argument of argparser.

If you want to change this behavior or add help text, choice limitation, and etc when setup argparse,
you can use ```@task.set_argument``` decorator and pass the same arguments you pass when using ```argparse```.
One requirement is that you must pass ```dest``` argument and speficy the argument to be connected between 
command line and the task function.

```python
@task
@task.set_argument('source', help='The source where you come from', choice=('Tokyo', 'Osaka'), dest='source')
@task.set_argument('--speed', '-s', help='The speed you wanna run', type=int, dest='speed')
def run(source, destination, speed=42):
    print('Run from {0} to {1} by speed={2}'.format(source, destination, speed))
```

And now you can only run from Tokyo or Osaka but cannot run from Kyoto
Also you must run in an int value speed.

For positional arguments, taskr matches its name and argument of function automatically.
But for optional arguments, you must assign ```dest``` to make taskr understand which argument of function
shoule map to.


### ```@task.pass_argparse_namespace``` decorator

If your task function has set ```pass_argparse_namespace``` by this decorator,
then all the argument of argparse should be decalred explicitly. (i.e. taskr won't discover for you automatically)
Also the argument passed into your task function is only the
[```namespace```](https://docs.python.org/3/library/argparse.html#argparse.Namespace) comes from argparse


```python
@task
@task.pass_argparse_namespace
@task.set_argument('start_time')
@task.set_argument('end_time')
def sleep(arguments):
    print('Sleep from {0.start_time} to {0.end_time}'.format(arguments))
```



## Usage - console & Color


### Color

```Color``` class in the console module helps you to show color output. It has:
* BLACK
* RED
* GREEN
* YELLOW
* BLUE
* MAGENTA
* CYAN
* WHITE

```python
from taskr import Color
print(Color.str('message', foreground=Color.RED, background=Color.YELLOW, light=True))
# message (RED bold text in YELLOW background)
```


### Console

The ```console``` module helps you to print color message on console.
```Console``` class takes a file-like object as its output destination and the ```console``` object is an instance
of that class which instantiate with [```sys.stdout```](https://docs.python.org/3/library/sys.html#sys.stdout)

```python
from taskr import console
console.show('Hello')
# Hello
console.show('Hello', bar_width=40)
# Hello ==================================
console.show('Hello', bar_width=40, bar_character='-')
Hello ----------------------------------
```

There are some shortcut functions which combines the ```Console.show``` and ```Color.str``` together, They are ```Console.info```, ```Console.error```, ```Console.success```, ```Console.highlight```, and ```Console.prompt```.
To add customized shortcut function named ```test```, inherite the Console class and add one of ```test_prefix```
and ```test_color```. The ```prefix``` will be attatched to the front of your message, and the ```color``` should
be a tuple like ```(Color.RED, False)``` (color, light_or_not)



## Usage - Contrib

### reader.CSVReader

It helps you to convert CSV content into Python's list of dictionaries.

We have a CSV file named ```sample.csv```

first name | last name | age
-----------|-----------|----
Hiro       | Sato      | 16
Junichi    | Masahiro  | 27

```python
from taskr.contrib.reader import CSVReader
print(CSVReader('sample.csv').content)
# [{'last name': 'Sato', 'age': '16', 'first name': 'Hiro'}, {'last name': 'Masahiro', 'age': '27', 'first name': 'Junichi'}]
```

### Misc

There are also a function to help you enable django support.
Check the source code for more features.
