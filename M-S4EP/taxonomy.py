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
    sqliteConnection = sqlite3.connect('db_prova.sqlite') # dalla connessione ottengo l'oggetto cursor
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

    query = "SELECT tech, periods,input_comm, ti_split FROM TechInputSplit"
    cursor.execute(query)
    input_split = cursor.fetchall()
    input_split_values = []
    for elem in input_split:
        if elem[0] in techs:
            input_split_values.append(elem)

    query = "SELECT tech, periods, output_comm, to_split FROM TechOutputSplit"
    cursor.execute(query)
    output_split = cursor.fetchall()
    output_split_values = []
    for elem in output_split:
        if elem[0] in techs:
            output_split_values.append(elem)

    print("First 10 of input split:")
    for i in range(0,10):
        print(input_split_values[i])

    print("\n\nFirst 10 of output split:")
    for i in range(0, 10):
        print(output_split_values[i])

    # normalize emissions GWP_100, TOT_CO2 in [tCO2eq/act] --> recall the function normalize
    for i, row in enumerate(emission_rows):
        emission_rows[i][5] = normalise_emission_factor_unit(row[5], row[6])

    # evaluation of emissions (sum of all GWP_100 for equivalent CO2 OR TOT_CO2 per each year, see "Code explanation" file on Notability)
    # sum is done as a single output may have multiple inputs
    tech_year_output_value_map = dict()
    # la mappa è come un vettore ma come indice ha una chiave, che può essere una stringa

    for row in emission_rows:
        if row[3] >= START_YEAR:
            key = str(row[2]) + "-" + str(row[3]) + "-" + str(row[4])
            value = float(row[5])
            if row[4] in CO2_OUTPUT:
                if row[0] == "TOT_CO2":
                    if key not in tech_year_output_value_map.keys(): # if key is not present yet, add it!
                        tech_year_output_value_map.update({key: 0.0})
                    tech_year_output_value_map.update({key: tech_year_output_value_map.get(key) + value})
            elif row[0] == "GWP_100":
                if key not in tech_year_output_value_map.keys():
                    tech_year_output_value_map.update({key: 0.0})
                tech_year_output_value_map.update({key: tech_year_output_value_map.get(key) + value})

    # save it on a csv file
    outFile = csv.writer(open("tech_year_value.csv", "w"))
    for key, value in tech_year_output_value_map.items():
        t = key.split("-")[0]
        y = key.split("-")[1]
        o = key.split("-")[2]
        outFile.writerow([t, y, o, value])

    # compare total emission with thresholds of Taxonomy and assign a flag premium (green or brown)
    # premium_emission is assigned (new column), premium_efficiency column is created, void, to be filled later

    # create a map valid_emission threshold
    emission_threshold_map = dict()
    for i, emission in enumerate(VALID_EMISSIONS):
        emission_threshold_map[emission] = 1 # vect[i]

    tech_year_output_diff_map = dict()
    for element in tech_year_output_value_map.items():
        key = element[0] # chiave tech anno output
        value = element[1]
        key_split = key.split("-") # vector
        tech = key_split[0]
        year = key_split[1]
        output = key_split[2]
        if output in CHANGING_THRESHOLD_OUTPUT and int(year) >= 2025:
            # the threshold is 0 => value - threshold = 0
            if value > 0:
                tech_year_output_diff_map.update({key: str(value) + "-" + "emission_penalty"}) # salvo la differenza + penalty/premium
            else:
                tech_year_output_diff_map.update({key: str(value) + "-" + "emission_premium"})
        else:
            if value > emission_threshold_map[str(output)]:
                tech_year_output_diff_map.update({key: str(value-emission_threshold_map[str(output)]) + "-" + "emission_penalty"})
            else:
                tech_year_output_diff_map.update({key: str(value-emission_threshold_map[str(output)]) + "-" + "emission_premium"})

    outFile = csv.writer(open("tech_year_output_diff_penalty.csv", "w"))
    for key, value in tech_year_output_diff_map.items():
        t = key.split("-")[0]
        y = key.split("-")[1]
        o = key.split("-")[2]
        v = value.split("-")[0]
        p = value.split("-")[1]
        outFile.writerow([t, y, o, v, p])

    # PART 2 : select useful parameters from Efficiency table
    query = "SELECT input_comm, tech, vintage, output_comm, efficiency, eff_notes FROM Efficiency"
    cursor.execute(query)
    efficiency_rows_tuples = cursor.fetchall()

    efficiency_rows = []
    for row in efficiency_rows_tuples:
        efficiency_rows.append(list(row))

    # before filtering efficiency according to output, check if there are tech producing output in valid_emission
    # but not present in emission map as they do not emit (ex. EV) -> add it to map and assign them an emission premium by default
    # se output = SNK_CO2 non fare niente! xk il premium a DAC l'hai già dato, e le altre tech con SNK_CO2 output sono LINKED e non hanno CostInv
    # elif row[3] in GREEN_H2 and row[1] not in emission_rows_filtered
    # (to award green H2 under the hypothesis to not consider average carbon intensity of electricity)

    techFromMap = []
    for element in tech_year_output_diff_map:
        techFromMap.append(element[0].split("-")[0])
    for element in efficiency_rows:
        output = element[3]
        year = element[2]
        tech = element[1]
        key = str(output) + "-" + str(year) + "-" + str(tech)
        if output in VALID_EMISSIONS and tech in techFromMap and output != "SNK_CO2":
            tech_year_output_diff_map.update({key: str(-5) + "-" + "emission_premium"})
        elif output in GREEN_H2 and tech in techFromMap:
            tech_year_output_diff_map.update({key: str(-5) + "-" + "emission_premium"})

    # filter for valid output - efficiency
    efficiency_rows_filtered = []
    for i, row in enumerate(efficiency_rows):
        if row[3] in VALID_EFFICIENCY:
            efficiency_rows_filtered.append(row)



except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
