from taskr import task


@task
@task.set_argument('source', help='The source where you come from', choices=('Tokyo', 'Osaka'))
@task.set_argument('--speed', '-s', help='The speed you wanna run', type=int, dest='speed')
def run(source, destination, speed=42, step_size=1):
    print('Run from {0} to {1} by speed={2} and step={3}'.format(source, destination, speed, step_size))


@task
@task.pass_argparse_namespace
@task.set_argument('start_time')
@task.set_argument('end_time')
def sleep(arguments):
    print('Sleep from {0.start_time} to {0.end_time}'.format(arguments))

if __name__ == '__main__':
    task.dispatch()
