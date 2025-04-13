from calender_tool import get_user_availability

# 傳入月份，格式是 "YYYY-MM"
result = get_user_availability("2025-06")

print("✅ Available Dates from Google Calendar:")
for day in result["available_dates"]:
    print(" -", day)
