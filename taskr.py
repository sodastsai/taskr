import argparse
import functools
import inspect


class Task(object):
    # Argument parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Action')

    @classmethod
    def dispatch(cls):
        args = cls.parser.parse_args()
        if hasattr(args, '__instance__'):
            kwargs = dict(vars(args))
            del kwargs['__instance__']
            args.__instance__(**kwargs)
        else:
            cls.parser.print_help()

    @classmethod
    def set_argument(cls, *args, **kwargs):
        def wrap(f):
            if not hasattr(f, 'arguments'):
                f.arguments = {}
            f.arguments[args[0]] = (args, kwargs)

            @functools.wraps(f)
            def wrapped(*w_args, **w_kwargs):
                return f(*w_args, **w_kwargs)
            wrapped.original_func = f

            return wrapped

        return wrap

    @classmethod
    def set_name(cls, name):
        def wrap(f):
            f.name = name

            @functools.wraps(f)
            def wrapped(*w_args, **w_kwargs):
                return f(*w_args, **w_kwargs)
            wrapped.original_func = f

            return wrapped

        return wrap

    def __init__(self, func):
        self.function = func
        # Register this task to argparse
        parser = self.subparsers.add_parser(hasattr(func, 'name') and func.name or func.__name__)
        parser.set_defaults(__instance__=self)

        # Get argument spec from original func for setting arguments
        original_func = func
        while hasattr(original_func, 'original_func'):
            original_func = original_func.original_func
        try:
            arg_spec = inspect.getfullargspec(original_func)
        except AttributeError:
            arg_spec = inspect.getargspec(original_func)

        # Parse argument spec into args list and kwargs dict
        if arg_spec.defaults:
            args = arg_spec.args[:-len(arg_spec.defaults)]
            kwargs = dict(zip(arg_spec.args[-len(arg_spec.defaults):], arg_spec.defaults))
        else:
            args = arg_spec.args
            kwargs = {}

        # Setting arguments
        manual_arguments = hasattr(func, 'arguments') and func.arguments or {}
        for arg_name in args:
            if arg_name in manual_arguments:
                arg_args, arg_kwargs = manual_arguments[arg_name]
                parser.add_argument(*arg_args, **arg_kwargs)
            else:
                parser.add_argument(arg_name)
        for kwarg_name, default_value in kwargs.items():
            arg_name = '--' + kwarg_name.replace('_', '-')
            if arg_name in manual_arguments:
                arg_args, arg_kwargs = manual_arguments[arg_name]
                parser.add_argument(*arg_args, **arg_kwargs)
            else:
                parser.add_argument(arg_name, default=default_value)

    def __call__(self, *args, **kwargs):
        self.function(*args, **kwargs)

    @classmethod
    def error(cls, message):
        cls.parser.error(message)

    @classmethod
    def exit(cls, status=0, message=None):
        cls.parser.exit(status, message)


# Decorator Export
task = Task


# ======================================================================================================================
# Utils: Print Console
# ======================================================================================================================

class Console(object):
    LIGHT = 1
    FOREGROUND = 30
    BACKGROUND = 40
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    @classmethod
    def color_str(cls, message, foreground=-1, background=-1, light=False):
        codes = []
        if light:
            codes.append(str(cls.LIGHT))
        if foreground >= 0:
            codes.append(str(cls.FOREGROUND + foreground))
        if background >= 0:
            codes.append(str(cls.BACKGROUND + background))
        return '\033[{0}m{1}\033[m'.format(';'.join(codes), message)

    @classmethod
    def error(cls, message):
        print(cls.color_str('😱  {0}'.format(message), cls.RED))

    @classmethod
    def success(cls, message):
        print(cls.color_str('🍺  {0}'.format(message), cls.GREEN))

    @classmethod
    def info(cls, message):
        print(cls.color_str('✈️  {0}'.format(message), cls.CYAN))

    @classmethod
    def prompt(cls, message):
        print(cls.color_str('👻  {0}'.format(message), cls.MAGENTA))

    @classmethod
    def highlight(cls, message):
        print(cls.color_str('🚬  {0}'.format(message), cls.CYAN, light=True))

    @classmethod
    def show(cls, message, foreground=-1, background=-1, light=False):
        print(cls.color_str(message, foreground, background, light))

# Function Export
console = Console
