def register_handlers(application):
    from .conversation import ConversationFlow
    conv = ConversationFlow()
    application.add_handler(conv.setup_build())
    # Need to add more handlers here as the bot grows