Feature: Handle database events
    In order to support storing a database
    As a developer
    We'll implement database reading and writing

    Scenario: Read database
        Given I have the database test.txt
        When I process it with Events.read
        Then I see 3 events

    Scenario Outline: Check events
        Given I have the database test.txt
        When I process it with Events.read
        Then I see event <n> contains <project>, <start> and <delta>

        Examples:
            | n | project  | start                     | delta   |
            | 0 | project  | 2011-05-04 08:00:00+00:00 | 1:00:00 |
            | 1 | project2 | 2011-05-04 09:15:00+00:00 | 0:15:00 |
            | 2 | project  | 2011-05-04 09:30:00+00:00 | 0:00:00 |

    Scenario: Write database
        Given I have the events from test.txt
        When I write it to a temp file
        Then I see an duplicate of test.txt

    Scenario: Store messages with events
        Given I have the database test.txt
        When I process it with Events.read
        When I check return value for calling last on result
        When I check message attribute of result
        Then I see the string 'finished'
