# Example commands for Set_Config.py interactive CLI

# Add services
add payment_service
add notification_service
add user_service
add analytics_service

# Set config key/value for environments
set payment_service base timeout 30
set payment_service base retries 3
set payment_service base currency USD
set payment_service production timeout 60
set payment_service production currency EUR
set payment_service staging timeout 45

set notification_service base provider email
set notification_service base enabled True
set notification_service production provider sms
set notification_service dev enabled False

set user_service base max_users 1000
set user_service base region us-east
set user_service production max_users 5000
set user_service test region eu-west

set analytics_service base enabled True
set analytics_service base interval 15
set analytics_service production interval 5
set analytics_service dev enabled False

# Add/replace entire environment config (JSON)
addenv payment_service qa '{"timeout": 50, "currency": "GBP"}'
addenv notification_service test '{"provider": "push", "enabled": true}'

# Show all configs for a service
show payment_service
show notification_service
show user_service
show analytics_service

# List all services
list

# Export a service's config to a JSON file
printjson payment_service
printjson notification_service

# Delete a service
delete analytics_service

# List again to confirm deletion
list
