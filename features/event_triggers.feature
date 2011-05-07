Feature: Handle event triggers
    In order to support managing events
    As a user
    We'll implement event starting and stopping

    Scenario: Start event
        Given I have the database test_not_running.txt
        When I process it with Events.read
        When I call start on result with project=project2
        When I check output for calling running on result
        Then I see the string 'project2'

    Scenario: Fail starting when currently running
        Given I have the database test.txt
        When I process it with Events.read
        When I call start on result with project=project2
        Then I receive ValueError

    Scenario: Stop event
        Given I have the database test.txt
        When I process it with Events.read
        When I call stop on result
        When I check output for calling running on result
        Then I see the string 'False'

    Scenario: Fail stopping when not currently running
        Given I have the database test_not_running.txt
        When I process it with Events.read
        When I call stop on result
        Then I receive ValueError
