def check_value(tech, output, input):
    # Transport sector
    output_check = ["TRA_ROA_LCV", "TRA_ROA_MTR", "TRA_ROA_HTR", "TRA_ROA_BUS", "TRA_ROA_CAR", "TRA_AVI_DOM",
                    "TRA_AVI_INT", "TRA_NAV_DOM", "TRA_NAV_INT", "TRA_RAIL_FRG", "TRA_RAIL_PSG"]
    # Power sector
    output_power = ["ELC_CEN", "ELC_DST", "HET"]
    # Biomass source
    input_bio = ["ELC_BLQ", "ELC_BGS", "ELC_SLB_RES", "ELC_SLB_VIR"]

    if output in output_check:
        if input == "TRA_ELC":
            return 24/100
        if input == "TRA_H2G" or input == "TRA_H2L" or input == "TRA_AMM":
            return 32/100
        else:
            return 5/100  # default value in TEMOA (SDR)
    if output in output_power and input != "ELC_IMP":
        if input in input_bio:
            return 10/100
        if input == "ELC_SOL":
            return 5.7/100
        if input == "ELC_WIN" and str("_OFF_") not in str(tech):
            return 7.6/100  # onshore wind
        if input == "ELC_WIN" and str("_OFF_") in str(tech):
            return 8.6/100  # offshore wind
        if input == "ELC_HYD":
            return 5.23/100
        if input == "ELC_COA" and tech != "ELC_COA_STM_H500MW_N":  # in this case HR = 20% from TEMOA DB
            return 6.69/100
        if input == "ELC_NGA":
            return 10/100
        if input == "ELC_BMU" and output != "HET":
            return 9.7/100
        if input == "ELC_BMU" and output == "HET":  # CHP plants with waste
            return 11.5/100
        if input == "ELC_GEO":
            return 10/100
        else:
            return 5/100  # default value in TEMOA (SDR)

