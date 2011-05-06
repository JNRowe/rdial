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

 Scenario Outline: Handle partial definition durations
    Given I have the string <string>
    When I process it with parse_delta
    Then I see the timedelta object <result>

  Examples:
    | string   | result  |
    | PT04H    | 4:00:00 |
    | PT04H30M | 4:30:00 |
    | PT30M    | 0:30:00 |
    | PT04H21S | 4:00:21 |
    | PT4H     | 4:00:00 |

 Scenario Outline: Handle durations including days
    Given I have the string <string>
    When I process it with parse_delta
    Then I see the timedelta object <result>

  Examples:
    | string  | result          |
    | P3DT04H | 3 days, 4:00:00 |
    | P3D     | 3 days, 0:00:00 |

  Scenario Outline: Produce ISO-8601 durations including days
    Given I have the timedelta object <timedelta>
    When I process it with format_delta
    Then I see the string <result>

  Examples:
    | timedelta        | result        |
    | 3 days, 4:00:00  | P3DT04H00M00S |
    | 3 days, 0:00:00  | P3DT00H00M00S |
    | 2 days, 22:00:00 | P2DT22H00M00S |
