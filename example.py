from taskr import task


@task
@task.set_group_argument('places', 'source', help='The source where you come from', choices=('Tokyo', 'Osaka'))
@task.set_group_argument('places', 'destination')
@task.set_argument('--speed', '-s', help='The speed you wanna run', type=int, dest='speed')
def run(source, destination, vehicle, speed=42, step_size=1):
    print('Run from {0} to {1} by vehicle={4} speed={2} and step={3}'
          .format(source, destination, speed, step_size, vehicle))


@task
@task.pass_argparse_namespace
@task.set_argument('start_time')
@task.set_argument('end_time')
def sleep(arguments):
    print('Sleep from {0.start_time} to {0.end_time}'.format(arguments))

if __name__ == '__main__':
    task.dispatch()
