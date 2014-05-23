from taskr import task

@task
@task.set_argument('source', help='The source where you come from', choices=('Tokyo', 'Osaka'))
@task.set_argument('--speed', '-s', help='The speed you wanna run', type=int)
def run(source, destination, speed=42):
    print('Run from {0} to {1} by speed={2}'.format(source, destination, speed))
   
if __name__ == '__main__':
    task.dispatch()
