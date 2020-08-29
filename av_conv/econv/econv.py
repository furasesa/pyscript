from .context import FileSelector
from .context import Probe
from .options import parse_option


def main():
    argoptions = parse_option()
    directory = vars(argoptions).get('directory')
    f = FileSelector(directory)



if __name__ == '__main__':
    main()
