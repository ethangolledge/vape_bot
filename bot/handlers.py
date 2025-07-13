def register_handlers(application):
    from .conversation import ConversationFlow
    conv = ConversationFlow()
    application.add_handler(conv.build())
    # Need to add more handlers here as the bot grows