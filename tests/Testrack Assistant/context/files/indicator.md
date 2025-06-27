# PG Admin
- Indicators postgres table can be found following this path:

    `Databases`: `test` ⟶ `Schemas`: `ford_clusters` ⟶ `Tables`: `Indicators`
    
    **Table structure**

    | name| logic | stss |
    | :--:    | :--: | :--: |
    | NAME_OF_THE_INDICATOR_IN_SRD | specific json | id from the stss table |

     ⭐ If the indicator has 'n' number of colors, it must be separated in 'n' rows in the table writing the name as follow example:

    `NEW_INDICATOR_COLOR1`

    `NEW_INDICATOR_COLOR2`


# JSON Structure:
```json
    {
    "diag": [list of strings],
    "type": string,
    "color": string,
    "generic": {
        "volt": [list of strings],
        "perso": {
            "ecu": string,
            "type": string,
            "feat_no": int,
            "feat_config": int
        },
        "config": logic expression string
    },
    "chime_id": int,
    "bulbcheck": string,
    "indicator": [
        {
        "name": string,
        "value": int
        }
    ],
    "icon_config": logic expression string,
    "etm_bulbcheck": bool,
    "logic_activation": [
        {
        "pwr": [list of strings],
        "type": string,
        "logic": {
            "logic": logic expression string,
            "override": {string : [list of int]}}
        },
    ],
    "warning_process_mask": string
    }
```
## Diagnostics 
🛠️ Under construction, **TBD**🛠️
- `"diag":` List of strings to define DID's, DTC's and RID's.

    **Optional:** Yes

    **Constraint:** No

    **default value:** null

   _Example:_
    ```json
        "diag": ["DID","DTC","RID"]
    ```

    or
    ```json
        "diag": null
    ```
## Type
🛠️ Under construction, **TBD**🛠️
- `"type":` String to determine if the indicator is TT_Fixed or RTT_Dedicated.

    **Optional:** No

    **Constraint:** "RTT_Dedicated", "TT_Fixed"

    **default value:** N/A

   _Example:_
    ```json
        "type": "TT_Fixed"
    ```
## Color
- `"color":` String to determine the color of the indicator.

    **Optional:** No

    **Constraint:** "Amber", "Green", "Grey", "Blue", "Red", "White"

    **default value:** N/A

   _Example:_
    ```json
        "color": "Amber"
    ```

## Generic
- `"generic":` Dictionary of objects that contains:

    | Generic objects |
    | :--:    | 
    | volt    |
    | perso   |
    | config  |

    ## Generic -> *voltage flags*
    - `"volt":` List of strings with the applicable voltage flags.

        **Optional:** Yes

        **Constraint:** "HVSD0", "HVSD1", "LVSD0", "LVSD1"

        **default value:** null

       _Example:_
        ```json
            "volt": ["HVSD0"] 
        ```
            
        or 
        ```json
            "volt": null
        ```

    ## Generic -> *personalization*
    🛠️ Under construction, **TBD**🛠️
    - `"Perso":` Dictionary to set personalization configurations if applicable for the indicator, contains: 


        | Personalization objects |
        | :--:    | 
        | ecu |
        | type |
        | feat_no |
        | feat_config |

        ## Generic -> *personalization* -> *ECU*
        - `"ecu":` String to indicate the ECU used to send the personalization signals.

            **Optional:** Yes

            **Constraint:** "HCM", "DSM", "BCM", "IPMA", "SCCM", "DDM", "CCM", "FCIM", "APIM", "APIM2"

            **default value:** null

           _Example:_
            ```json
                "ecu": "BCM"
            ```
            or 
            ```json 
                "ecu": null
            ```
        ## Generic -> *personalization* -> *type*
        - `"type":` String to indicate the personalization type.

            **Optional:** Yes

            **Constraint:** "Cluster", "Generic", "Dedicated"

            **default value:** null

           _Example:_
            ```json
                "type": "Generic"
            ```
            or 
            ```json 
                "type": null
            ```
        ## Generic -> *personalization* -> *feat number*
        - `"feat_no":` Integer to indicate the personalization feat number value.

            **Optional:** Yes

            **Constraint:** No

            **default value:** null

           _Example:_
            ```json
                "feat_no": "2055"
            ```
            or 
            ```json 
                "feat_no": null
            ```

        ## Generic -> *personalization* -> *feat configuration*
        - `"feat_config":` Integer to indicate the personalization feat config value.

            **Optional:** Yes

            **Constraint:** No

            **default value:** null

           _Example:_
            ```json
                "feat_config": "1"
            ```
            or 
            ```json 
                "feat_config": null
            ```

    ## Generic -> *configuration*
    - `"config":` String for logic expression made by the [logical combinations API](https://testrack.visteon.com/api/test/docs#/default/generate_logic_post) to enable the indicator with VOPS.

        **Optional:** Yes

        **Constraint:** No

        **default value:** true

       _Example:_
        ```json
            "config": "_PT_HYBRID_2 = 0 AND _AUTO_STOP_START = 1"
        ```
        or 
        ```json 
            "config": "true"
        ```
## Chime ID
🛠️ Under construction, **TBD**🛠️
- `"chime_id":` Integer to indicate the id for the indicator chime.

    **Optional:** Yes

    **Constraint:** No

    **default value:** null

   _Example:_
    ```json
        "chime_id": 53
    ```
    or 
    ```json 
        "chime_id": null
    ```

## Bulbcheck
- `"bulbcheck":` String to indicate the **keyword** of the bulbcheck time. 

    **Optional:** Yes

    **Constraint:** "TT_PBC_COUNT_1", "TT_PBC_COUNT_2"

    **default value:** null

   _Example:_
    ```json
        "bulbcheck": "TT_PBC_COUNT_1"
    ```
    or 
    ```json 
        "bulbcheck": null
    ```
## Indicator
- `"indicator":` List of objects that contains:

    | Indicator objects |
    | :--:    | 
    | name    |
    | value   |

    ## Indicator -> *name*
    - `"name":` String to indicate the class name of the indicator based on the class names in the [Classes server](http://10.137.60.200:5000/icons/info), to request a detection to [AI server](http://10.137.60.200:5000/ui/#/Detect/telltales.detect) (can be more than 1 indicator in special cases splitted by ",").

        **Optional:** No

        **Constraint:** No

        **default value:** N/A

       _Example:_
        ```json
            "name": "HIGH_BEAM_INDICATOR_LIGHT"
        ```
    ## Indicator -> *value*
    🛠️ Under construction, **TBD**🛠️
    - `"value":` Integer to set the [icon_config](#icon-configuration) value to display the [name](#indicator-name) specific icon in case that 2 or more different indicators are applicable for the same feature that can be changed through configuration VOPS.

        **Optional:** Yes

        **Constraint:** No

        **default value:** null

       _Example:_
        ```json
            "value": 1
        ```
        or
        ```json
            "value": null
        ```
## Icon configuration
🛠️ Under construction, **TBD**🛠️
- `"icon_config":` String for logic expression to set the configuration with [value](#indicator-value) for an specific icon indicated in [name](#indicator-name) in case that 2 or more different indicators are applicable for the same feature that can be changed through configuration VOPS.

    **Optional:** Yes

    **Constraint:** No

    **default value:** true

   _Example:_
    ```json
        "icon_config": "_HMI_DAT_LANE_ASSIST_FEATURE_SYMBOL"
    ```
    or
    ```json
        "icon_config": "true"
    ```
## Engineering test mode bulbcheck
🛠️ Under construction, **TBD**🛠️
- `"etm_bulbcheck":` Boolean to indicate if the etm bulbcheck is applicable to the indicator.

    **Optional:** No

    **Constraint:** No

    **default value:** N/A

   _Example:_
    ```json
        "etm_bulbcheck": true
    ```

## Logic activations
- `"logic_activation":` List of objects that contains:

    | Logic activation objects |
    | :--:    | 
    | pwr    |
    | type  |
    | logic  |

    ## Logic activations -> *power modes*
    - `"pwr":` List of power modes applicable to the indicator.

        **Optional:** No

        **Constraint:** "Run", "Start", "Off", "Acc", "Unknown", "Invalid"

        **default value:** N/A

       _Example:_
        ```json
            "pwr": ["Run","Start"]
        ```
    ## Logic activations -> *type*
    - `"type":` String to indicates if the indicator turns On solid, or flashing.

        **Optional:** No

        **Constraint:** "On", "Flash1", "Flash2", "Flash3", "Flash4", "Flash5", "Flash6", "Flash7", "Flash8"

        **default value:** N/A

       _Example:_
        ```json
            "type": "On"
        ```
    ## Logic activations -> *logic*
    - `"logic":` Dictionary of objects that contains:
        | Logic objects |
        | :--:    | 
        | logic |
        | override |

        ## Logic activations -> *logic* -> *logic*
        - `"logic":` String for logic expression made by the [logical combinations API](https://testrack.visteon.com/api/test/docs#/default/generate_logic_post) to activate the indicator.

            **Optional:** No

            **Constraint:** No

            **default value:** N/A

           _Example:_
            ```json
                "logic": "(DrvAntiLckLamp_D_Rq).nreceived = true OR (DrvAntiLckLamp_D_Rq).missing = true OR (DrvAntiLckLamp_D_Rq).value = 1"
            ```
        ## Logic activations -> *logic* -> *override*
        - `"override":` Dictionary that contains signal and specific `On` and `Off` values to be used in the logical combinations.

            **Optional:** Yes

            **Constraint:** No

            **default value:** {}

           _Example:_
            ```json
                "override": {"DrvAntiLckLamp_D_Rq": [0,1]}
            ```
            or
            ```json
                "override": {}
            ```

## Warning process mask
- `"warning_process_mask":` String to indicate the **keyword** of the warning process mask time.

    **Optional:** Yes

    **Constraint:** "WARNING_PROCESS_MASK_TIMER", "SIDEMARKER_PROCESS_MASK_TIMER"

    **default value:** null

   _Example:_
    ```json
        "warning_process_mask": "WARNING_PROCESS_MASK_TIMER"
    ```
    or
    ```json
        "warning_process_mask": null
    ```

# yml. File
For more details on how to configure options and features for test execution, refer to [Test Configuration](/README.md#test-configuration) within README file.