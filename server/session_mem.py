class SessionMemoryStore:
    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id, chain, vectorstore, tmpdir):
        self.sessions[session_id] = {
            "chain": chain,
            "vectorstore": vectorstore,
            "tmpdir": tmpdir
            }
    def get_session(self, session_id):
        return self.sessions.get(session_id)
    def delete_session(self, session_id):
        return self.sessions.pop(session_id, None)
    def session_exists(self, session_id):
        return session_id in self.sessions