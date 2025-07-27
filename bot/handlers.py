from .conversation import ConversationFlow

def register_handlers(application):
    conv = ConversationFlow()
    application.add_handler(conv.setup_build())
    application.add_handler(conv.help())
    application.add_handler(conv.start()) 