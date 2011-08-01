Feature: Handle database schema updates
    In order to support reading a database
    As a developer
    We'll implement old database schema reading

    Scenario: Support databases without message fields on events
        Given I have the database test_no_message_field.txt
        When I process it with Events.read
        When I check return value for calling last on result
        When I check message attribute of result
        Then I see the string 'None'