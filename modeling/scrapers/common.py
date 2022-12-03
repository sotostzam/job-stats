TYPES = {
    0: '\u001b[38;5;102m' + 'DEBUG'   + '\033[0m',
    1: '\u001b[38;5;38m'  + 'INFO'    + '\033[0m',
    2: '\u001b[38;5;166m' + 'WARNING' + '\033[0m',
    3: '\u001b[38;5;196m' + 'ERROR'   + '\033[0m',
    4: '\u001b[38;5;46m'  + 'SUCCESS' + '\033[0m'
}

def pprint(msg: str, type: int, prefix: str = '', as_str = False) -> (str | None):
    '''
    Pretty prints a message with decorators and colors.

    Args:
    -------
    - `msg`    (str):           The message to be printed
    - `type`   (int):           The type of message. There are 5 types: (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `SUCCESS`)
    - `prefix` (str, optional): Text to be printed as a prefix
    - `as_str` (bool):          Instead of printing, return the decorated text as a string

    Returns:
    -------
    - `str`:  The decorated string containing prefixes and colors
    - `None`: Prints the decorated text directly in the terminal
    '''

    if not as_str:
        print(f'[{prefix}][{TYPES[type]}]: {msg}')
    else:
        return f'[{prefix}][{TYPES[type]}]: {msg}'

def print_progress(iteration: int, total: int, length = 50, msg_complete = '') -> None:
    '''
    Prints a progress bar in the terminal.

    Args:
    -------
    - `iteration`    (int):           The current value of the progress range
    - `total`        (int):           The maximum value of the progress range
    - `length`       (int, optional): The length of the progress bar in the terminal
    - `msg_complete` (str, optional): Text to be printed after the progress range has been completed
    '''

    percentage = ("{0:.1f}").format(100 * (iteration / float(total)))
    completed = int(length * iteration // total)
    percentage_bar = '█' * completed + '-' * (length - completed)
    text = f'\rProgress: |{percentage_bar}| {percentage}% | Processed {iteration}/{total}'
    
    print(text, end="\r")

    # Clean progress line and print desired message
    if iteration == total: 
        print(' ' * len(text), end="\r")
        print(msg_complete)
