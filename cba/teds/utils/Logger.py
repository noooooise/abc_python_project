
import logging


def getLogger(logLevel=logging.INFO):
    """
    getLogger() will return a Logger (logging.Logger) object with a Stream Handler.

    Example: getLogger().info("Example Log Message (%s)", someVariable)

    If you're going to be creating more than one log entry you should store and reuse the returned object.

    This interface ensures that chained imports don't attach superfluous Stream Handlers.
    """

    logger = logging.getLogger("cba")

    # Add a CBA Log Handler if there isn't one already
    if logger.handlers == []:
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(logLevel)
        logger.addHandler(streamHandler)
        logger.info("Created CBA Log Handler.")
    else:
        logger.handlers[0].setLevel(logLevel)

    logger.setLevel(logLevel)

    return logger;
