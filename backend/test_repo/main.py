def greet(name):
    if name:
        return "hello " + name
    return "hello"


def run_flow(user):
    msg = greet(user)
    return msg
