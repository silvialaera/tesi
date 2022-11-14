import sqlite3
import csv

# normalize emissions in [tCO2eq/act]
def normalise_emission_factor_unit(val, unit):
    num = unit.split("/")[0]
    if num == "[t" or num == "t":
        return val
    elif num == "[kt" or num == "kt":
        return val * 1000


# output values to be taken (from Output column in "EU Taxonomy for TEMOA sectors" sheet in Excel file)
# for DAC, IND, H2, TRA sectors
VALID_EMISSIONS = ["SNK_CO2", "H2_DT", "H2_CT", "H2_CU", "IND_NM_CLK", "IND_NM_CMT",
                   "IND_NF_ALU", "IND_IS_BOF", "IND_IS_EAF", "IND_CH_HVC", "IND_CH_BTX", "IND_CH_MTH",
                   "IND_CH_AMM", "TRA_RAIL_PSG", "TRA_RAIL_FRG", "TRA_ROA_BUS", "TRA_ROA_CAR", "TRA_ROA_LCV",
                   "TRA_ROA_2WH", "TRA_ROA_HTR", "TRA_ROA_MTR"]

# output having TSC in gCO2 and not gCO2 equivalent (no GWP evaluation is needed). include also DAC (SNK_CO2)
CO2_OUTPUT = ["SNK_CO2", "IND_CH_AMM", "TRA_ROA_CAR", "TRA_ROA_LCV", "TRA_ROA_2WH", "TRA_ROA_HTR", "TRA_ROA_MTR"]

# thresholds to be respected for emissions. For each element of valid_emission vector, a threshold is assigned below.
# unit of measure tCO2/tOutput for H2, IND, while for TRA is in tCO2/Bv*km

GREEN_H2 = ["H2_DTE", "H2_CUE", "H2_CTE"]
LHV_H2 = 120  # MJ/kg a 0°C
H2_LIM = 0.95  # 0,95 tCO2e/tOutput per taxonomy
H2_EM = H2_LIM*1e-3/(LHV_H2*1e3/1e9)
CLK_EM = 0.766*1e3  # da tCO2/tOutput in ktCO2/MtOutput
CMT_EM = 0.498*1e3  # da tCO2/tOutput in ktCO2/MtOutput
AL_EM = 1.514*1e3  # da tCO2/tOutput in ktCO2/MtOutput
BOF_EM = 0.325*1e3  # da tCO2/tOutput in ktCO2/MtOutput
EAF_EM = 0.3175*1e3  # da tCO2/tOutput in ktCO2/MtOutput
HVC_EM = 0.702*1  # da tCO2/tOutput in ktCO2/MtOutput


EMISSION_THRESHOLD = [0, H2_EM, H2_EM, H2_EM, CLK_EM, CMT_EM,
                      AL_EM, BOF_EM, EAF_EM,  ]

CHANGING_THRESHOLD_OUTPUT = ["TRA_RAIL_PSG", "TRA_RAIL_FRG", "TRA_ROA_BUS", "TRA_ROA_CAR", "TRA_ROA_LCV"]

# for CCUS, H2 and IND needing efficiency, RES, COM, Storage
VALID_EFFICIENCY = ["DMY_OUT", "COM_SH", "COM_WH", "COM_SC", "COM_LG", "ELC_DST", "H2_CTE", "H2_CUE", "H2_DT",
                    "H2_DTE", "H2_CU", "H2_CT", "IND_NF_EC", "IND_CH_CHL", "IND_CH_OLF",
                    "RES_PC_MO", "RES_PC_SN", "RES_PC_SO", "RES_PH_MO", "RES_PH_SN", "RES_PH_SO", "RES_PW_MO",
                    "RES_PW_SN", "RES_PW_SO", "RES_WH", "RES_SH_SO", "RES_SH_MO", "RES_SH_SN", "RES_SH_MN", "RES_SC", "RES_LG",
                    "RES_WH", "RES_INS_C", "RES_INS_MO", "RES_INS_SN", "RES_INS_SO",
                    "BIO_BIN", "BIO_BMU", "BIO_DST", "BIO_ETH", "BIO_GAS", "BIO_SLB_RES", "BIO_SLB_VIR"]
H2_CONSUMPTION = 50  # MWh/tOutput
H2_EFF = 1/(H2_CONSUMPTION*3.6e-6/(LHV_H2*1000/1e9))
COM_HP_EFF = 3.3  # efficiency threshold Heat pumps in COM and RES (PJ/PJ) for SH, WH, SC
COM_LG_EFF = 5.5  # efficiency threshold lighting (COM_LG is in PJ, RES_LG is in Glm)
AL_EFF = 1/(15.29*3.6e-6*1e6)  # MWh/t primary Al for IND_NF_EC. AL demand is in Mt
CHL_EFF = 1/(2.75*3.6e-6*1e6)  # MWh/t primary Chl for IND_NF_EC. CH demand is in Mt
RES_SH_SO_factor = 1.9395
RES_SH_MO_factor = 2.6602
RES_SH_SN_factor = 1.9395
RES_SH_MN_factor = 1.9395
RES_SC_factor = 14.7257
RES_LG_EFF = 20 # default choice by me for lighting in RES
EFFICIENCY_THRESHOLD = [0, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_LG_EFF, 0, H2_EFF, H2_EFF, H2_EFF,
                        H2_EFF, H2_EFF, H2_EFF, AL_EFF, CHL_EFF, 0,
                        COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF,
                        COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF/RES_SH_SO_factor, COM_HP_EFF/RES_SH_MO_factor, COM_HP_EFF/RES_SH_SN_factor, COM_HP_EFF/RES_SH_MN_factor, COM_HP_EFF/RES_SC_factor, RES_LG_EFF,
                        0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0]
START_YEAR = 2022

try:
    sqliteConnection = sqlite3.connect('db_prova.sqlite')  # dalla connessione ottengo l'oggetto cursor
    cursor = sqliteConnection.cursor()
    print("Database created and Successfully Connected to SQLite")

    # PART 1: select useful parameters from EmissionActivity table
    # input comm forse non mi serve!! CHECK
    query = "SELECT emis_comm, input_comm, tech, vintage, output_comm, emis_act, emis_act_units FROM EmissionActivity"
    cursor.execute(query)
    emission_rows_tuples = cursor.fetchall() # fetchall to extract result of last query exectued

    emission_rows = []
    for row in emission_rows_tuples:
        emission_rows.append(list(row))  # da vettore di tuple a vettore di vettori

    techs = []
    for i, elem in enumerate(emission_rows):
        techs.append(elem[2])

    query = "SELECT tech, periods, input_comm, ti_split FROM TechInputSplit ORDER BY tech"
    cursor.execute(query)
    temp = cursor.fetchall()
    input_split_values = []
    for elem in temp:
        if elem[0] in techs:
            input_split_values.append(elem)

    query = "SELECT tech, periods, output_comm, to_split FROM TechOutputSplit ORDER BY tech"
    cursor.execute(query)
    temp = cursor.fetchall()
    output_split_values = []
    for elem in temp:
        if elem[0] in techs:
            output_split_values.append(elem)

    # tech, periods, input_comm
    query = "SELECT TechInputSplit.tech, TechInputSplit.periods, Efficiency.input_comm FROM TechInputSplit, Efficiency WHERE TechInputSplit.tech IN (SELECT tech FROM TechInputSplit GROUP BY tech, periods, regions HAVING COUNT(*) = 1) AND Efficiency.tech = TechInputSplit.tech and Efficiency.vintage = TechInputSplit.periods ORDER BY TechInputSplit.tech"
    cursor.execute(query)
    temp_input_values = cursor.fetchall()

    # tech, periods, output_comm
    query = "SELECT TechOutputSplit.tech, TechOutputSplit.periods, Efficiency.output_comm FROM TechOutputSplit, Efficiency WHERE TechOutputSplit.tech IN (SELECT tech FROM TechOutputSplit GROUP BY tech, periods, regions HAVING COUNT(*) = 1) AND Efficiency.tech = TechOutputSplit.tech and Efficiency.vintage = TechOutputSplit.periods"
    cursor.execute(query)
    temp_output_values = cursor.fetchall()

    input_split_values_temp = input_split_values
    for temp_elem in temp_input_values:
        found = False
        for i, elem in enumerate(input_split_values):
            if elem[0] == temp_elem[0] and elem[1] == temp_elem[2] and elem[2] == temp_elem[2]:
                found = True
        if not found:
            val = 0
            for i, elem in enumerate(input_split_values):
                if elem[0] == temp_elem[0] and elem[1] == temp_elem[1] and temp_elem[2] != elem[2]: # ENTRA QUI UNA SOLA VOLTA VERIFICA!!!!!
                    val = float(elem[3])
            if val != 0:
                input_split_values_temp.append([temp_elem[0], temp_elem[1], temp_elem[2], 1-val])
    input_split_values = input_split_values_temp
    for el in input_split_values:
        print(el)

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)