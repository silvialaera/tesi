def check_value(output, input):
    # Transport sector
    output_check = ["TRA_ROA_LCV", "TRA_ROA_MTR", "TRA_ROA_HTR", "TRA_ROA_BUS", "TRA_ROA_CAR", "TRA_AVI_DOM",
                    "TRA_AVI_INT", "TRA_NAV_DOM", "TRA_NAV_INT", "TRA_RAIL_FRG", "TRA_RAIL_PSG"]
    if output in output_check:
        if input == "TRA_ELC":
            return 24/100
        if input == "TRA_H2G" or input == "TRA_H2L" or input == "TRA_AMM":
            return 32/100