import pytest


def test_get_all_activities(client):
    """Test GET /activities returns all activities with correct structure"""
    # Arrange - no special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 14  # Based on current activities
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Basketball Team"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert email in response.json()["message"]


def test_signup_increases_participant_count(client):
    """Test that signup actually adds participant to the list"""
    # Arrange
    email = "counttest@mergington.edu"
    activity = "Programming Class"

    # Act
    client.post(f"/activities/{activity}/signup", params={"email": email})
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert email in data[activity]["participants"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity returns 404"""
    # Arrange
    email = "student@mergington.edu"
    activity = "Nonexistent Activity"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_duplicate_email(client):
    """Test signup with email already registered returns 400"""
    # Arrange
    activity = "Chess Club"
    # Get existing participant
    activities_response = client.get("/activities")
    existing_email = activities_response.json()[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_full(client):
    """Test signup when activity is at max capacity returns 400"""
    # Arrange - fill up an activity
    activity = "Tennis Club"  # max 10, currently has some
    activities_response = client.get("/activities")
    current_count = len(activities_response.json()[activity]["participants"])
    max_participants = activities_response.json()[activity]["max_participants"]

    # Fill up the remaining spots
    for i in range(max_participants - current_count):
        client.post(f"/activities/{activity}/signup",
                   params={"email": f"fill{i}@mergington.edu"})

    # Now try to add one more
    email = "overflow@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]


def test_unregister_success(client):
    """Test successful unregister from an activity"""
    # Arrange
    email = "removeme@mergington.edu"
    activity = "Gym Class"
    # First sign up
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    assert email in response.json()["message"]


def test_unregister_removes_participant(client):
    """Test that unregister actually removes participant from the list"""
    # Arrange
    email = "removecount@mergington.edu"
    activity = "Programming Class"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    client.delete(f"/activities/{activity}/signup", params={"email": email})
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert email not in data[activity]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister for non-existent activity returns 404"""
    # Arrange
    email = "student@mergington.edu"
    activity = "Fake Activity"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_student_not_signed_up(client):
    """Test unregister for student not in activity returns 400"""
    # Arrange
    email = "notsigned@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]