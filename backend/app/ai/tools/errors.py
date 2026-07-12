class ToolExecutionError(Exception):
    """
    Raised by an app.ai.tools function when it can't complete its job for
    a reason the *user* can fix (missing doctor name, bad date, unknown
    interaction type). Nodes catch this and surface `str(exc)` directly
    as the assistant's reply — it's written to be read, not logged.
    """
