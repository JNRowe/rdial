Feature: Filter database events
    In order to support operate on subsets of events
    As a user
    We'll implement basic filtering methods

    Scenario: Fetch events for specific task
        Given I have the database test.txt
        When I process it with Events.read
        When I check return value for calling for_task on result with task=task2
        Then I see 1 events

    Scenario: Fetch events for specific year
        Given I have the database date_filtering.txt
        When I process it with Events.read
        When I check return value for calling for_date on result with year=2011
        Then I see 2 events

    Scenario: Fetch events for specific month
        Given I have the database date_filtering.txt
        When I process it with Events.read
        When I check return value for calling for_date on result with year=2011, month=1
        Then I see 1 events

    Scenario: Fetch events for specific day
        Given I have the database date_filtering.txt
        When I process it with Events.read
        When I check return value for calling for_date on result with year=2011, month=3, day=1
        Then I see 1 events
