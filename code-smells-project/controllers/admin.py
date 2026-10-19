from domain.validation import object_data


class AdminController:
    def __init__(self, repository):
        self.repository = repository

    def counts(self):
        return self.repository.counts()

    def inspect(self, payload):
        return self.repository.inspect(object_data(payload).get("sql"))

    def reset(self):
        self.repository.reset()
