def check_power(count, tot_emission, input, year, output):
    # Linear interpolation is performed between actual limit (@2025) and @2050 ones
    LIM_2025_ELC = 100/3.6  # da gCO2/kWh in ktCO2/PJ
    LIM_2025_HET = 30/3.6
    LIM_2025_CHP = (LIM_2025_ELC+LIM_2025_HET)/2  # average value and not weighted one based on TOS as typically CHP has TOS around 0.4 and 0.6
    LIM_2050 = 0
    LIM_LIQ_2025 = 94*(1-0.85)  # da MtCO2/MJ in ktCO2/PJ for liquid biomass
    LIM_SG_ELC_2025 = 198*(1-0.85)
    LIM_SG_HET_2025 = 87*(1-0.85)
    LIM_SG_CHP_2025 = (LIM_SG_ELC_2025+LIM_SG_HET_2025)/2

    INPUT_CHP = ["ELC_GEO", "ELC_NGA"]
    INPUT_CHP_BIO = ["ELC_BGS", "ELC_SLB_RES", "ELC_SLB_VIR", "ELC_BMU"]

    if input == "ELC_SOL":
        return 1
    # for biomass see fossil fuel comparator in RED II, distinguish liquid from solid&gaseous biomass
    if input == "ELC_BLQ":
        LIM_LIQ_YEAR = LIM_LIQ_2025+((int(year)-2025)/(2050-2025))*(LIM_2050-LIM_LIQ_2025)
        if float(tot_emission) <= float(LIM_LIQ_YEAR):
            return 1
        else:
            return 0
    if (input == "ELC_BGS" or input == "ELC_SLB_RES" or input == "ELC_SLB_VIR" or input == "ELC_BMU") and output != "HET" and count == 1:
        LIM_SG_ELC_YEAR = LIM_SG_ELC_2025+((int(year)-2025)/(2050-2025))*(LIM_2050-LIM_SG_ELC_2025)
        if float(tot_emission) <= float(LIM_SG_ELC_YEAR):
            return 1
        else:
            return 0
    if (input == "ELC_BGS" or input == "ELC_SLB_RES" or input == "ELC_SLB_VIR" or input == "ELC_BMU") and output == "HET" and count == 1:
        LIM_SG_HET_YEAR = LIM_SG_HET_2025+((int(year)-2025)/(2050-2025))*(LIM_2050-LIM_SG_HET_2025)
        if float(tot_emission) <= float(LIM_SG_HET_YEAR):
            return 1
        else:
            return 0
    if input in INPUT_CHP_BIO and count > 1:
        LIM_YEAR = LIM_SG_CHP_2025+((int(year)-2025)/(2050-2025))*(LIM_2050-LIM_SG_CHP_2025)
        if float(tot_emission) <= float(LIM_YEAR):
            return 1
        else:
            return 0
    if input == "ELC_WIN" or input == "ELC_HYD" or input == "ELC_GEO" or input == "ELC_NGA" and output != "HET" and count == 1:
        LIM_YEAR = LIM_2025_ELC+((int(year)-2025)/(2050-2025))*(LIM_2050-LIM_2025_ELC)
        if float(tot_emission) <= float(LIM_YEAR):
            return 1
        else:
            return 0
    if input == "ELC_WIN" or input == "ELC_HYD" or input == "ELC_GEO" or input == "ELC_NGA" and output == "HET" and count == 1:
        LIM_YEAR = LIM_2025_HET+((int(year)-2025)/(2050-2025))*(LIM_2050-LIM_2025_HET)
        if float(tot_emission) <= float(LIM_YEAR):
            return 1
        else:
            return 0
    if input in INPUT_CHP and count > 1:
        LIM_YEAR = LIM_2025_CHP+((int(year)-2025)/(2050-2025))*(LIM_2050-LIM_2025_CHP)
        if float(tot_emission) <= float(LIM_YEAR):
            return 1
        else:
            return 0
    if input == "ELC_COA" or input == "ELC_GASDER" or input == "ELC_HHC" or input == "ELC_OIL":
        return 0