import os

import click

from boom.utils.title_helper import get_title

commands_folder = os.path.join(os.path.dirname(__file__), 'commands')

class BaseCommands(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(commands_folder):
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, cmd_name):
        ns = {}
        command = None
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name[0])]
        if not matches:
            return None
        elif len(matches) == 1:
            command = matches[0]
        else:
            ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))
        fn = os.path.join(commands_folder, command + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['run']


@click.command(cls=BaseCommands)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)

    ctx.obj['TEMPLATES_FOLDER'] = os.path.join(os.path.dirname(__file__), 'templates')

    click.echo(get_title())


if __name__ == '__main__':
    cli()
