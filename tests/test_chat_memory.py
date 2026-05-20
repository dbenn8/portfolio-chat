def test_session_store_and_retrieve():
    from app.chat import get_history, save_turn

    save_turn("test-session-1", "user", "What did Dan build with n8n?")
    save_turn("test-session-1", "assistant", "Dan built MBO Listing Sync...")

    history = get_history("test-session-1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_session_isolation():
    from app.chat import get_history, save_turn

    save_turn("session-a", "user", "Question A")
    save_turn("session-b", "user", "Question B")

    assert len(get_history("session-a")) >= 1
    assert any(m["content"] == "Question A" for m in get_history("session-a"))


def test_session_max_history():
    from app.chat import get_history, save_turn, MAX_HISTORY

    session = "overflow-session-unique"
    for i in range(MAX_HISTORY + 5):
        save_turn(session, "user", f"Message {i}")

    history = get_history(session)
    assert len(history) <= MAX_HISTORY
