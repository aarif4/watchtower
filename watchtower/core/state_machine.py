# this is a stateless state machine. It will be used in spiders where 
# yielding will continue the usage

class StateMachine:
    state_handlers = {}
    startState = None
    endStateNames = []
    logger = None

    def __init__(self, logger):
        self.logger = logger

    def add_state(self, stateName, handler, is_endState=False):
        stateName = stateName.upper()
        self.state_handlers[stateName] = handler

        if is_endState:
            self.endStateNames.append(stateName)
            self.logger.info('added %s state, is an EndState' % (stateName,))
        else:
            self.logger.info('added %s state' % (stateName,))

    def set_startState(self, name):
        self.startState = name.upper()
        self.logger.info('Made %s state into a StartState' % (name.upper(),))

    def run_state(self, curState, data):
        self.logger.info('About to run %s state' % (curState.upper(),))
        handler = self.state_handlers[curState.upper()]
        data = handler(data, self.logger)
        
        return data

    def reached_endState(self, curState):
        if curState.upper() in self.endStateNames:
            self.logger.info('Reached %s, which is an EndState' % (curState.upper(),))
            return True
        else:
            return False
