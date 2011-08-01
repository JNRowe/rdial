Feature: Query database events
    In order to support querying the database
    As a user
    We'll implement simple query methods

    Scenario: List tasks
        Given I have the database test.txt
        When I process it with Events.read
        When I check output for calling tasks on result
        Then I see the string "['task', 'task2']"

    Scenario: Currently running event
        Given I have the database test.txt
        When I process it with Events.read
        When I check output for calling running on result
        Then I see the string 'task'

    Scenario: No currently running event
        Given I have the database test_not_running.txt
        When I process it with Events.read
        When I check output for calling running on result
        Then I see the string 'False'

    Scenario: Sum event durations in database
        Given I have the database test_not_running.txt
        When I process it with Events.read
        When I check output for calling sum on result
        Then I see the string '2:15:00'
