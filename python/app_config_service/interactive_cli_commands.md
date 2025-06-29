# Example commands for interactive CLI testing
first use this command
python -m app_config_service.cli                          

NOW
# Add services
add-service payment_service
add-service notification_service
add-service user_service
add-service analytics_service

# Set base configurations
set-base payment_service '{"timeout": 30, "retries": 3, "currency": "USD"}'
set-base notification_service '{"provider": "email", "enabled": true}'
set-base user_service '{"max_users": 1000, "region": "us-east"}'
set-base analytics_service '{"enabled": true, "interval": 15}'

# Set environment-specific configurations
set-env payment_service production '{"timeout": 60, "currency": "EUR"}'
set-env payment_service staging '{"timeout": 45}'
set-env notification_service production '{"provider": "sms"}'
set-env notification_service dev '{"enabled": false}'
set-env user_service production '{"max_users": 5000}'
set-env user_service test '{"region": "eu-west"}'
set-env analytics_service production '{"interval": 5}'
set-env analytics_service dev '{"enabled": false}'

# List all services
list-services

# Describe each service
describe-service payment_service
describe-service notification_service
describe-service user_service
describe-service analytics_service

# Export a service's config to JSON
print-service-json payment_service
print-service-json notification_service

# Delete a service
delete-service analytics_service

# List again to confirm deletion
list-services
