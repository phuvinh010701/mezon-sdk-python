from mezon.models import UserProfileUpdatedEvent


def test_user_profile_updated_event_allows_partial_payload() -> None:
    event = UserProfileUpdatedEvent.model_validate(
        {
            "user_id": "184067432015",
            "avatar": "https://example.com/avatar.png",
            "clan_id": "1779484504377790464",
        }
    )

    assert event.user_id == 184067432015
    assert event.display_name is None
    assert event.avatar == "https://example.com/avatar.png"
    assert event.about_me is None
    assert event.channel_id is None
    assert event.clan_id == 1779484504377790464
