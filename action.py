

class Action():
    
    none = 'None'
    open = 'OPEN'
    close = 'CLOSE'
    update = 'UPDATE'
    delete = 'DELETE'
    change_state = 'CHANGE STATE'
    reset_state = 'RESET STATE'

class Command():

    def __init__(self, action, position):

        self.action = action
        self.position = position
