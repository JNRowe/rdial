Feature: Query database events
    In order to support querying the database
    As a user
    We'll implement simple query methods

    Scenario: List tasks
        Given I have the database test/
        When I apply the Events.read method
        When I check output for calling tasks on result
        Then I see the string "[u'task', u'task2']"

    Scenario: Currently running event
        Given I have the database test/
        When I apply the Events.read method
        When I check output for calling running on result
        Then I see the string 'task'

    Scenario: No currently running event
        Given I have the database test_not_running/
        When I apply the Events.read method
        When I check output for calling running on result
        Then I see the string 'False'

    Scenario: Sum event durations in database
        Given I have the database test_not_running/
        When I apply the Events.read method
        When I check output for calling sum on result
        Then I see the string '2:15:00'
