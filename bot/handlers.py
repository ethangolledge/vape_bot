from .conversation import ConversationFlow
from .data_transfer import DuckDBManager

def register_handlers(application, db: DuckDBManager):
    conv = ConversationFlow(db)
    application.add_handler(conv.setup_build())
    application.add_handler(conv.help())
    application.add_handler(conv.start()) 