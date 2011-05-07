Feature: Handle ISO-8601 datetimes
  In order to support ISO-8601 datetimes
  As a developer
  We'll implement datetime parsing and formatting

  Scenario Outline: Parse ISO-8601 datetimes
    Given I have the string <string>
    When I process it with parse_datetime
    Then I see the datetime object <result>

  Examples:
    | string               | result                    |
    | 2011-05-04T08:00:00Z | 2011-05-04 08:00:00+00:00 |
    | 2011-05-04T09:15:00Z | 2011-05-04 09:15:00+00:00 |

  Scenario Outline: Produce ISO-8601 datetimes
    Given I have the datetime object <datetime>
    When I process it with isodate.datetime_isoformat
    Then I see the string <result>

  Examples:
    | datetime            | result               |
    | 2011-05-04 08:00:00 | 2011-05-04T08:00:00Z |
    | 2011-05-04 09:15:00 | 2011-05-04T09:15:00Z |
