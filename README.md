# Vape Bot

A personal project to track vaping habits using a Telegram bot interface.

## Project Structure

### `/bot`
Contains core Telegram bot functionality:
- `conversation.py`: Manages user interaction flows
- `extractors.py`: Handles Telegram update data extraction
- `handlers.py`: Routes bot commands to appropriate handlers

### `/data`
- `models.py`: Defines data structures that bridge Telegram data to DuckDB storage
- `database.py`: Management and transfer of the DuckDB database

## Features
- User setup for tracking vaping habits
- Configurable reduction goals (percentage or fixed number)
- Habit tracking and updates
- DuckDB integration for data persistence

## Deployment Goal
Run containerised in Docker on a server for 24/7 availability.
Track vape habits, with the goal of reducing reliance on vaping.

## Next Steps
- Implement comprehensive testing with Pytest
- Standardize error handling across conversation states
- Establish consistent logging practices
- Containerization with Docker

## Tech Stack
- Python
- python-telegram-bot
- DuckDB
- Docker (planned)

## Status
Active development - Core functionality working, focusing on reliability improvements.