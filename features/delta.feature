Feature: Handle ISO-8601 durations
  In order to support ISO-8601 durations
  As a developer
  We'll implement duration parsing and formatting

  Scenario Outline: Parse ISO-8601 durations
    Given I have the string <string>
    When I process it with parse_delta
    Then I see the timedelta object <result>

  Examples:
    | string      | result  |
    | PT04H30M21S | 4:30:21 |
    | PT00H12M01S | 0:12:01 |

  Scenario Outline: Produce ISO-8601 durations
    Given I have the timedelta object <timedelta>
    When I process it with format_delta
    Then I see the string <result>

  Examples:
    | timedelta | result      |
    | 4:30:21   | PT04H30M21S |
    | 0:12:01   | PT00H12M01S |

  Scenario: Parse null duration strings
    Given I have an empty string
    When I process it with parse_delta
    Then I see the timedelta object 0:00:00

  Scenario: Handle empty duration
    Given I have the timedelta object 0:00:00
    When I process it with format_delta
    Then I see an empty string
