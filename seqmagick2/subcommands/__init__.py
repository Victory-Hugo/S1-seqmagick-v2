commands = 'convert', 'info', 'mogrify', 'quality_filter', \
        'extract_ids', 'backtrans_align', 'split'


def itermodules(root=__name__):
    for command in commands:
        yield (command.replace('_', '-'),
               __import__('%s.%s' % (root, command), fromlist=[command]))
