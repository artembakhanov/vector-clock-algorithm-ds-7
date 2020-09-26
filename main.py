from multiprocessing import Process, Pipe


def get_pipe(pid1, pid2, pipes):
    """
    Get pipe for communicating between pid1 and pid2.
    Pipes should be either array or dict with appropriate elements indices.
    Example: pipe[pid1][pid2] - pipe that is used by pid1 for communicating with pid2
    """
    return pipes[pid1][pid2]


def max_vector(vector, new_vector):
    """
    Return vector that is composed of maximum elements
    """
    if len(vector) != len(new_vector):
        raise ValueError

    for i in range(len(vector)):
        vector[i] = max(vector[i], new_vector[i])


def event(pid, vector, *args):
    """
    Just simple event
    """
    vector[pid] += 1
    print(f"[{pid}] - EVENT - {vector}")


def send_message(pid, vector, pipes, recv_pid):
    """
    Send message to recv_pid
    """
    vector[pid] += 1
    get_pipe(pid, recv_pid, pipes).send(("Some message", vector))
    print(f"[{pid}] - SENDMES TO {recv_pid} - {vector}")


def recv_message(pid, vector, pipes, send_pid):
    """
    Recv message from send_pid
    """
    message, new_vector = get_pipe(pid, send_pid, pipes).recv()
    max_vector(vector, new_vector)
    vector[pid] += 1
    print(f"[{pid}] - RECVMES FROM {send_pid} - {vector}")


actions = {
    'event': event,
    'send_message': send_message,
    'recv_message': recv_message,
}


def process(pid, max_processes, pipes, actions_list):
    vector = [0] * max_processes
    for action in actions_list:
        actions[action if isinstance(action, str) else action[0]](pid, vector, pipes, *action[1:])
    print(f"Final {pid} - {vector}")


# define pipes
pipe01, pipe10 = Pipe()
pipe12, pipe21 = Pipe()
pipes = {
    0: {1: pipe01},
    1: {0: pipe10, 2: pipe12},
    2: {1: pipe21}
}

# define processes and their actions
process1 = Process(target=process, args=(
    0, 3, pipes,
    [
        ('send_message', 1),
        ('send_message', 1),
        'event',
        ('recv_message', 1),
        'event', 'event',
        ('recv_message', 1)
    ]))
process2 = Process(target=process, args=(
    1, 3, pipes,
    [
        ('recv_message', 0),
        ('recv_message', 0),
        ('send_message', 0),
        ('recv_message', 2),
        'event',
        ('send_message', 0),
        ('send_message', 2),
        ('send_message', 2),
    ]))
process3 = Process(target=process, args=(
    2, 3, pipes,
    [
        ('send_message', 1),
        ('recv_message', 1),
        'event',
        ('recv_message', 1),
    ]))

if __name__ == '__main__':
    # start processes
    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()
