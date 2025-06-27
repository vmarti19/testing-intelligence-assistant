
# Warning Definition

The follow table show the propierties according to the warning type column.

### Table 1. Warning Type Definition
| Type Description   | Description                        | Warning Type   |   NWD Time | Ack in New   | Instant Ack   |   OWC Time | Ack in Old   | Required Display Time   | Timeout Acknowledged   |
|:-------------------|:-----------------------------------|:---------------|-----------:|:-------------|:--------------|-----------:|:-------------|:------------------------|:-----------------------|
| Global Alert Types | Non-Resetable Global Alert         | NGA            |          2 | No           | No            |          4 | No           | No                      | No                     |
| Global Alert Types | Resetable Global Alert             | RGA            |          2 | Yes          | No            |          4 | No           | No                      | No                     |
| Warning Types      | Non-Resetable                      | NR             |          2 | No           | No            |          4 | No           | No                      | No                     |
| Warning Types      | Single Cycle*                      | SC*            |          2 | Yes          | No            |          4 | Yes          | No                      | No                     |
| Warning Types      | Single Cycle                       | SC            |          2 | Yes          | No            |          4 | Yes          | No                      | No                     |
| Warning Types      | Temporary Alert*                   | TA*            |          2 | Yes          | No            |          4 | Yes          | No                      | Yes                    |
| Warning Types      | Temporary Alert                    | TA             |          2 | Yes          | No            |          4 | Yes          | Yes                     | Yes                    |
| Other              | Reconfigurable Telltale            | RTT            |        nan | nan          | nan           |        nan | nan          | nan                     | nan                    |
| Other              | Telltale / Reconfigurable Telltale | TT/RTT         |        nan | nan          | nan           |        nan | nan          | nan                     | nan                    |

The following parameters in the JSON structure should be populated based on the "Warning type" field (e.g., NGA, RGA, NR, SC*, SC, TA*, TA, RTT, or TT/RTT) as defined in Table 1:

- **"nwd_time"**: This parameter corresponds to the "NWD Time" column. The value is provided in seconds and must be converted to milliseconds.

- **"owc_time"**: This parameter corresponds to the "OWC Time" column. Like nwd_time, the value is in seconds and must be converted to milliseconds. However, for warning types TA and TA*, the value from Table 1 should be disregarded. Instead, this parameter must be set according to the specifications defined in the Warnings Generic Application GM.

- **"timeout_ack"**: This parameter maps to the "Timeout Acknowledged" column. If the value is "Yes", set timeout_ack to true; if "No", set it to false.

- **"ok_button"**: This parameter maps to the "Ack In New" column. If the value is "Yes", set ok_button to true; if "No", set it to false.

