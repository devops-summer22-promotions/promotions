Feature: The promotions management service back-end
    As a Marketing Manager
    I need a RESTful promotions management service
    So that I can keep track of all my promotions that I am responsible for managing

Background:
    Given the following promotions
        | name          | type              | discount  | customer  | start_date    | end_date      |
        | flash bogo    | BUY_ONE_GET_ONE   | 0         | -1        | 2022-08-01    | 2022-08-02    |
        | vip 75 off    | VIP               | 75        | 123       | 2022-08-01    | 2022-08-07    |
        | aug freeship  | FREE_SHIPPING     | 0         | -1        | 2022-08-01    | 2022-08-31    |
        | 25 off sale   | PERCENT_DISCOUNT  | 25        | -1        | 2022-08-15    | 2022-08-22    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotions RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Promotion
    When I visit the "Home Page"
    And I set the "Name" to "Half-off sale!"
    And I select "Percent Discount" in the "Type" dropdown
    And I set the "Discount" to "50"
    And I set the "Customer" to "-1"
    And I set the "Start Date" to "08-01-2022"
    And I set the "End Date" to "09-01-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Type" field should be empty
    And the "Discount" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Half-off sale!" in the "Name" field
    And I should see "Percent Discount" in the "Type" dropdown
    And I should see "50" in the "Discount" field
    And I should see "2022-08-01" in the "Start Date" field
    And I should see "2022-09-01" in the "End Date" field

# Scenario: List all pets
#     When I visit the "Home Page"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: Search for dogs
#     When I visit the "Home Page"
#     And I set the "Category" to "dog"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should not see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: Search for available
#     When I visit the "Home Page"
#     And I select "True" in the "Available" dropdown
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should see "sammy" in the results
#     And I should not see "leo" in the results

# Scenario: Update a Pet
#     When I visit the "Home Page"
#     And I set the "Name" to "fido"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the "Name" field
#     And I should see "dog" in the "Category" field
#     When I change "Name" to "Boxer"
#     And I press the "Update" button
#     Then I should see the message "Success"
#     When I copy the "Id" field
#     And I press the "Clear" button
#     And I paste the "Id" field
#     And I press the "Retrieve" button
#     Then I should see the message "Success"
#     And I should see "Boxer" in the "Name" field
#     When I press the "Clear" button
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "Boxer" in the results
#     And I should not see "fido" in the results

# Scenario: Delete a Pet
#     When I visit the "Home Page"
#     And I set the "Name" to "fido"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     When I copy the "Id" field
#     And I press the "Delete" button
#     Then I should see the message "Pet has been Deleted!"
