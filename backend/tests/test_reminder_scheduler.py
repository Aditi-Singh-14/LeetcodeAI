from datetime import datetime, timezone

import pytest


def test_due_timezones_includes_local_11pm_zone():
    from alerts.progress_checker import due_timezones

    zones = due_timezones(datetime(2026, 1, 1, 17, 30, tzinfo=timezone.utc))

    assert "Asia/Kolkata" in zones


@pytest.mark.asyncio
async def test_find_due_reminder_users_filters_by_timezone(app_module):
    from alerts import progress_checker

    app_module.db.preferences.records.extend(
        [
            {
                "user_id": "due-user",
                "is_opted_in": True,
                "timezone": "Asia/Kolkata",
                "whatsapp_number": "+911234567890",
            },
            {
                "user_id": "not-due-user",
                "is_opted_in": True,
                "timezone": "UTC",
                "whatsapp_number": "+10000000000",
            },
        ]
    )
    progress_checker.db = app_module.db

    users = await progress_checker.find_due_reminder_users(
        datetime(2026, 1, 1, 17, 30, tzinfo=timezone.utc)
    )

    assert [user["user_id"] for user in users] == ["due-user"]


@pytest.mark.asyncio
async def test_enqueue_due_reminders_dedupes_jobs(app_module, mocker):
    from alerts import progress_checker

    app_module.db.preferences.records.append(
        {
            "user_id": "due-user",
            "is_opted_in": True,
            "timezone": "Asia/Kolkata",
            "whatsapp_number": "+911234567890",
        }
    )
    progress_checker.db = app_module.db

    task = mocker.patch(
        "tasks.reminder_tasks.check_user_progress_and_alert_task.delay",
        autospec=True,
    )

    now = datetime(2026, 1, 1, 17, 30, tzinfo=timezone.utc)
    first = await progress_checker.enqueue_due_reminders(now)
    second = await progress_checker.enqueue_due_reminders(now)

    assert first["queued"] == 1
    assert second["queued"] == 0
    task.assert_called_once_with("due-user")

@pytest.mark.asyncio
async def test_enqueue_due_reminders_allows_new_reminder_windows(app_module, mocker):
    from alerts import progress_checker

    app_module.db.preferences.records.append(
        {
            "user_id": "due-user",
            "is_opted_in": True,
            "timezone": "Asia/Kolkata",
            "whatsapp_number": "+911234567890",
        }
    )
    progress_checker.db = app_module.db

    task = mocker.patch(
        "tasks.reminder_tasks.check_user_progress_and_alert_task.delay",
        autospec=True,
    )

    first_window = datetime(2026, 1, 1, 17, 30, tzinfo=timezone.utc)
    second_window = datetime(2026, 1, 2, 17, 30, tzinfo=timezone.utc)

    first = await progress_checker.enqueue_due_reminders(first_window)
    second = await progress_checker.enqueue_due_reminders(second_window)

    assert first["queued"] == 1
    assert second["queued"] == 1
    assert task.call_count == 2
@pytest.mark.asyncio
async def test_enqueue_due_reminders_deduplication_is_window_specific(
    app_module, mocker
):
    from alerts import progress_checker

    app_module.db.preferences.records.append(
        {
            "user_id": "due-user",
            "is_opted_in": True,
            "timezone": "Asia/Kolkata",
            "whatsapp_number": "+911234567890",
        }
    )
    progress_checker.db = app_module.db

    task = mocker.patch(
        "tasks.reminder_tasks.check_user_progress_and_alert_task.delay",
        autospec=True,
    )

    window_one = datetime(2026, 1, 1, 17, 30, tzinfo=timezone.utc)
    window_two = datetime(2026, 1, 1, 18, 30, tzinfo=timezone.utc)

    await progress_checker.enqueue_due_reminders(window_one)
    await progress_checker.enqueue_due_reminders(window_two)

    assert task.call_count == 2
