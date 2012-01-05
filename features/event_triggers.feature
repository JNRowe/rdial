Feature: Handle event triggers
    In order to support managing events
    As a user
    We'll implement event starting and stopping

    Scenario: Start event
        Given I have the database test_not_running.txt
        When I apply the Events.read method
        When I call start on result with task=task2
        When I check output for calling running on result
        Then I see the string 'task2'

    Scenario: Fail starting when currently running
        Given I have the database test.txt
        When I apply the Events.read method
        When I call start on result with task=task2
        Then I receive ValueError

    Scenario: Stop event
        Given I have the database test.txt
        When I apply the Events.read method
        When I call stop on result
        When I check output for calling running on result
        Then I see the string 'False'

    Scenario: Stop event with message
        Given I have the database test.txt
        When I apply the Events.read method
        When I call stop on result with message=test
        When I check return value for calling last on result
        When I check message attribute of result
        Then I see the string 'test'

    Scenario: Fail stopping when not currently running
        Given I have the database test_not_running.txt
        When I apply the Events.read method
        When I call stop on result
        Then I receive ValueError
