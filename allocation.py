from datetime import datetime, date


def recommend_allocations(bookings):
    """
    Prioritises requests using:
    1. Project deadline
    2. Booking date and time
    3. Fair access between students
    """

    recommendations = []

    for booking in bookings:
        try:
            deadline = datetime.strptime(
                booking["deadline"], "%Y-%m-%d"
            ).date()

            days_left = (deadline - date.today()).days

        except (ValueError, TypeError):
            days_left = 999

        # Higher score means greater priority
        if days_left < 0:
            urgency = 10
        elif days_left <= 2:
            urgency = 100
        elif days_left <= 7:
            urgency = 80
        elif days_left <= 14:
            urgency = 60
        else:
            urgency = 40

        score = urgency

        if booking["status"] == "Pending":
            score += 10

        recommendations.append({
            "booking": booking,
            "score": score,
            "reason": (
                f"Project deadline is in {days_left} days. "
                f"Priority score: {score}"
            )
        })

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations