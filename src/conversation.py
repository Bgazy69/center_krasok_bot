from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str
    content: str


class ConversationStore:
    """Хранит контекст диалога по user_id (последние N сообщений)."""

    def __init__(self, max_messages: int = 10) -> None:
        self._max_messages = max_messages
        self._store: dict[int, deque[ChatMessage]] = defaultdict(
            lambda: deque(maxlen=max_messages)
        )

    def add(self, user_id: int, role: str, content: str) -> None:
        self._store[user_id].append(ChatMessage(role=role, content=content))

    def get_history(self, user_id: int) -> list[ChatMessage]:
        return list(self._store[user_id])

    def clear(self, user_id: int) -> None:
        self._store.pop(user_id, None)
