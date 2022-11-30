import sqlite3
import csv
from PowerSectorTaxonomy import check_power

# normalize emissions in [tCO2eq/act]
def normalise_emission_factor_unit(val, unit):
    num = unit.split("/")[0]
    if num == "[t" or num == "t":
        return val / 1000
    elif num == "[kt" or num == "kt":
        return val


# output values to be taken (from Output column in "EU Taxonomy for TEMOA sectors" sheet in Excel file)
# for DAC, IND, H2, TRA sectors
VALID_EMISSIONS = ["SNK_CO2", "H2_DT", "H2_CT", "H2_CU", "IND_NM_CLK", "IND_NM_CMT",
                   "IND_NF_ALU", "IND_IS_BOF", "IND_IS_EAF", "IND_CH_HVC", "IND_CH_BTX", "IND_CH_MTH",
                   "IND_CH_AMM", "TRA_RAIL_PSG", "TRA_RAIL_FRG", "TRA_ROA_BUS", "TRA_ROA_CAR", "TRA_ROA_LCV",
                   "TRA_ROA_2WH", "TRA_ROA_HTR", "TRA_ROA_MTR",
                   "ELC_CEN", "ELC_DST", "HET"]

# diversify the power sector, as it needs the input to be controlled
POWER_OUTPUT = ["ELC_CEN", "ELC_DST", "HET"]

# output having TSC in gCO2 and not gCO2 equivalent (no GWP evaluation is needed). include also DAC (SNK_CO2)
CO2_OUTPUT = ["SNK_CO2", "IND_CH_AMM", "TRA_ROA_CAR", "TRA_ROA_LCV", "TRA_ROA_2WH", "TRA_ROA_HTR", "TRA_ROA_MTR"]

# thresholds to be respected for emissions. For each element of valid_emission vector, a threshold is assigned below.

GREEN_H2 = ["H2_DTE", "H2_CUE", "H2_CTE"]

LHV_H2 = 120  # MJ/kg a 0°C
H2_LIM = 0.95  # 0,95 tCO2e/tOutput per taxonomy
H2_EM = H2_LIM * 1e-3 / (LHV_H2 * 1e3 / 1e9)
CLK_EM = 0.766 * 1e3  # da tCO2/tOutput in ktCO2/MtOutput
CMT_EM = 0.498 * 1e3  # da tCO2/tOutput in ktCO2/MtOutput
AL_EM = 1.514 * 1e3  # da tCO2/tOutput in ktCO2/MtOutput
BOF_EM = 0.325 * 1e3  # da tCO2/tOutput in ktCO2/MtOutput
EAF_EM = 0.3175 * 1e3  # da tCO2/tOutput in ktCO2/MtOutput
HVC_EM = 0.702 * 1e3  # da tCO2/tOutput in ktCO2/MtOutput
BTX_EM = 0.0295 * 1e3
MTH_EM = 0.512 * 1e3
AMM_EM = 1 * 1e3
TRA_EM = 50  # (già ktCO2/Bvkm)
RAIL_FRG_EM = 50.77 * 1e4  # CHECK sui PJ
TR_EM = 118.73 * 10   # (per TRA_ROA_HTR, TRA_ROA_MTR * 0.5). 10 tons in average carried by a vehicle

EMISSION_THRESHOLD = [0, H2_EM, H2_EM, H2_EM, CLK_EM, CMT_EM,
                      AL_EM, BOF_EM, EAF_EM, HVC_EM, BTX_EM, MTH_EM,
                      AMM_EM, TRA_EM * 1.7, RAIL_FRG_EM * 0.5, TRA_EM * 1.7, TRA_EM, TRA_EM * 1.7,
                      0, TR_EM * 0.5, TR_EM * 0.5,
                      0, 0, 0]

CHANGING_THRESHOLD_OUTPUT = ["TRA_RAIL_PSG", "TRA_ROA_BUS", "TRA_ROA_CAR", "TRA_ROA_LCV"]

# for CCUS, H2 and IND needing efficiency, RES, COM, Storage
VALID_EFFICIENCY = ["DMY_OUT", "COM_SH", "COM_WH", "COM_SC", "COM_LG", "ELC_DST", "H2_CTE", "H2_CUE", "H2_DT",
                    "H2_DTE", "H2_CU", "H2_CT", "IND_CH_CHL", "IND_CH_OLF",
                    "RES_PC_MO", "RES_PC_SN", "RES_PC_SO", "RES_PH_MO", "RES_PH_SN", "RES_PH_SO", "RES_PW_MO",
                    "RES_PW_SN", "RES_PW_SO", "RES_WH", "RES_SH_SO", "RES_SH_MO", "RES_SH_SN", "RES_SH_MN", "RES_SC",
                    "RES_LG",
                    "RES_WH", "RES_INS_C", "RES_INS_MO", "RES_INS_SN", "RES_INS_SO",
                    "BIO_BIN", "BIO_BMU", "BIO_DST", "BIO_ETH", "BIO_GAS", "BIO_SLB_RES", "BIO_SLB_VIR"]

HEAT_PUMP = ["COM_SH", "COM_WH", "COM_SC",  "RES_PC_MO", "RES_PC_SN", "RES_PC_SO",
             "RES_PH_MO", "RES_PH_SN", "RES_PH_SO", "RES_PW_MO",
             "RES_PW_SN", "RES_PW_SO", "RES_WH"]

# ADD electricity commodities
ELC_TYPES = ["AGR_ELC", "COM_ELC", "RES_ELC", "TRA_ELC", "IND_ELC", "ELC_CEN", "ELC_DST"]

H2_CONSUMPTION = 50   # MWh/tOutput
H2_EFF = 1 / (H2_CONSUMPTION * 3.6e-6 / (LHV_H2 * 1000 / 1e9))
COM_HP_EFF = 3.3  # efficiency threshold Heat pumps in COM and RES (PJ/PJ) for SH, WH, SC
COM_LG_EFF = 5.5  # efficiency threshold lighting (COM_LG is in PJ, RES_LG is in Glm)
RES_LG_EFF = 15  # default choice by me for lighting in RES, compliant with tech chosen in COM
CHL_EFF = 1 / (2.75 * 3.6e-6 * 1e6)  # MWh/t primary Chl for IND_NF_EC. CH demand is in Mt
RES_SH_SO_factor = 1.9395
RES_SH_MO_factor = 2.6602
RES_SH_SN_factor = 1.9395
RES_SH_MN_factor = 1.9395
RES_SC_factor = 14.7257

OUTPUT_ELIGIBLE = ["DMY_OUT", "COM_WH", "RES_WH", "ELC_DST", "H2_CT", "H2_DT", "H2_CU", "RES_SH_SN", "RES_SH_SO", "RES_SH_MO", "RES_SH_MN"]

UNIQUE_OUTPUT = ["DMY_OUT", "ELC_DST", "H2_CT", "H2_DT", "H2_CU"]  # for those output competitors are not easy to find.
# the competitor of a sink of CO2 producing DMY_OUT is not UPS[...] producing the same DMY_OUT
# the same is for ELC_DST, and for H2 here for storage but storage not compete with other H2 producers. Or, better, they do not deserve a penalty.

INPUT_ELIGIBLE = ["SNK_CO2", "COM_SOL", "RES_SOL", "ELC_SOL", "H2_CT", "H2_DT", "H2_CU", "RES_SOL"]

ELIGIBLE_DEFAULT = ["RES_INS_C", "RES_INS_MO", "RES_INS_SN", "RES_INS_SO",
                    "BIO_BIN", "BIO_BMU", "BIO_DST", "BIO_ETH", "BIO_GAS", "BIO_SLB_RES", "BIO_SLB_VIR"]

RES_FACTOR_NAME = ["RES_SH_SO", "RES_SH_MO", "RES_SH_SN", "RES_SH_MN", "RES_SC"]

RES_FACTOR_VALUE = [RES_SH_SO_factor, RES_SH_MO_factor, RES_SH_SN_factor, RES_SH_MN_factor, RES_SC_factor]

EFFICIENCY_THRESHOLD = [0, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_LG_EFF, 0, H2_EFF, H2_EFF, H2_EFF,
                        H2_EFF, H2_EFF, H2_EFF, CHL_EFF, 0,
                        COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF,
                        COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF, COM_HP_EFF,
                        RES_LG_EFF,
                        COM_HP_EFF, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0]

START_YEAR = 2025  # milestone year in which EU Taxonomy starts being applied

try:
    sqliteConnection = sqlite3.connect('db_prova.sqlite')
    cursor = sqliteConnection.cursor()
    print("Database created and Successfully Connected to SQLite")

    # PART 1: Emissions
    # select useful parameters from EmissionActivity table
    query = "SELECT emis_comm, input_comm, tech, vintage, output_comm, emis_act, emis_act_units FROM EmissionActivity"
    cursor.execute(query)
    emission_rows_tuples = cursor.fetchall()  # fetchall to extract result of last query exectued

    emission_rows = []
    for row in emission_rows_tuples:
        emission_rows.append(list(row))  # da vettore di tuple a vettore di vettori --> easier

    # tech in EmissionActivity table
    techs = []
    for i, elem in enumerate(emission_rows):
        techs.append(elem[2])

    # looking for tech whose output is in valid_emission
    techs_emission = []
    for elem in emission_rows:
        if elem[4] in VALID_EMISSIONS:
            techs_emission.append(elem[2])

    # take TechInputSplit and TechOutputSplit for those tech
    query = "SELECT tech, periods, input_comm, ti_split FROM TechInputSplit ORDER BY tech"
    cursor.execute(query)
    temp = cursor.fetchall()
    input_split_values = []
    for elem in temp:
        if elem[0] in techs:
            input_split_values.append(elem)

    # TechOutput values not taken only for techs in EmissionActivity, as it will be useful later for efficiency
    query = "SELECT tech, periods, output_comm, to_split FROM TechOutputSplit ORDER BY tech"
    cursor.execute(query)
    output_split_values = cursor.fetchall()

    # for each period, select techs having more than one input in efficiency, but only one expressed in TechInputSplit
    # WHERE technologies fall into the group defined by GROUP BY
    query = "SELECT TechInputSplit.tech, TechInputSplit.periods, Efficiency.input_comm FROM TechInputSplit, Efficiency WHERE TechInputSplit.tech IN (SELECT tech FROM TechInputSplit GROUP BY tech, periods, regions HAVING COUNT(*) = 1) AND Efficiency.tech = TechInputSplit.tech and Efficiency.vintage = TechInputSplit.periods ORDER BY TechInputSplit.tech"
    cursor.execute(query)
    temp_input_values = cursor.fetchall()

    # for each period, select techs having only one input expressed in TechOutputSplit. now the name of every input is saved
    query = "SELECT TechOutputSplit.tech, TechOutputSplit.periods, Efficiency.output_comm FROM TechOutputSplit, Efficiency WHERE TechOutputSplit.tech IN (SELECT tech FROM TechOutputSplit GROUP BY tech, periods, regions HAVING COUNT(*) = 1) AND Efficiency.tech = TechOutputSplit.tech and Efficiency.vintage = TechOutputSplit.periods"
    cursor.execute(query)
    temp_output_values = cursor.fetchall()

    # extend input (TechInputSplit does not have all of them for each tech)
    input_split_values_temp = input_split_values
    for temp_elem in temp_input_values:
        found = False
        for i, elem in enumerate(input_split_values):
            if elem[0] == temp_elem[0] and elem[1] == temp_elem[2] and elem[2] == temp_elem[2]:
                found = True
        if not found:  # if that input has not been found
            val = 0
            for i, elem in enumerate(input_split_values):
                if elem[0] == temp_elem[0] and elem[1] == temp_elem[1] and temp_elem[2] != elem[2]:  # enter here just one time. Verified.
                    val = float(elem[3])
            if val != 0:
                input_split_values_temp.append([temp_elem[0], temp_elem[1], temp_elem[2], 1 - val])
    input_split_values = input_split_values_temp

    # extend output
    output_split_values_temp = output_split_values
    for temp_elem in temp_output_values:
        found = False
        for i, elem in enumerate(output_split_values):
            if elem[0] == temp_elem[0] and elem[1] == temp_elem[2] and elem[2] == temp_elem[2]:
                found = True
        if not found:
            val = 0
            for i, elem in enumerate(output_split_values):
                if elem[0] == temp_elem[0] and elem[1] == temp_elem[1] and temp_elem[2] != elem[2]:  # ENTRA QUI UNA SOLA VOLTA VERIFICA!!!!!
                    val = float(elem[3])
            if val != 0:
                output_split_values_temp.append([temp_elem[0], temp_elem[1], temp_elem[2], 1 - val])
    output_split_values = output_split_values_temp

    # evaluate whether sum(TechInputSplit) or sum(TechOutputSplit) of techs is != 1. In that case, normalize
    tech_year_inputSum_map = dict()
    for elem in input_split_values:
        key = str(elem[0]) + "-" + str(elem[1])
        if key not in tech_year_inputSum_map:
            tech_year_inputSum_map.update({key: 0})
        tech_year_inputSum_map.update({key: tech_year_inputSum_map.get(key) + float(elem[3])})
    input_split_values_temp = input_split_values
    input_split_values = []
    for row in input_split_values_temp:
        input_split_values.append(list(row))  # from vector of tuples to vector of vectors
    for elem in input_split_values:
        key = str(elem[0]) + "-" + str(elem[1])
        if key in tech_year_inputSum_map.keys():
            val = tech_year_inputSum_map.get(key)
            if val != 1:
                elem[3] = elem[3] / val

    tech_year_outputSum_map = dict()
    for elem in output_split_values:
        key = str(elem[0]) + "-" + str(elem[1])
        if key not in tech_year_outputSum_map:
            tech_year_outputSum_map.update({key: 0})
        tech_year_outputSum_map.update({key: tech_year_outputSum_map.get(key) + float(elem[3])})
    output_split_values_temp = output_split_values
    output_split_values = []
    for row in output_split_values_temp:
        output_split_values.append(list(row))  # from vector of tuples to vector of vectors
    for elem in output_split_values:
        key = str(elem[0]) + "-" + str(elem[1])
        if key in tech_year_outputSum_map.keys():
            val = tech_year_outputSum_map.get(key)
            if val != 1:
                elem[3] = elem[3] / val

    # coming back to EmissionActivity table -------
    # normalize emissions GWP_100, TOT_CO2 in [tCO2eq/act] --> recall the function normalize
    for i, row in enumerate(emission_rows):
        emission_rows[i][5] = normalise_emission_factor_unit(row[5], row[6])

    # create maps for TechInputSplit and TechOutputSplit
    input_split_values_map = dict()
    output_split_values_map = dict()
    for elem in input_split_values:
        input_split_values_map.update({str(elem[0]) + "-" + str(elem[1]) + "-" + elem[2]: float(elem[3])})
    for elem in output_split_values:
        output_split_values_map.update({str(elem[0]) + "-" + str(elem[1]) + "-" + elem[2]: float(elem[3])})

    tech_year_value_map = dict()
    tech_in = []
    for elem in input_split_values_map.items():
        tech_in.append(elem[0].split("-")[0])
    tech_out = []
    for elem in output_split_values_map.items():
        tech_out.append(elem[0].split("-")[0])

    # if cascade for analysing all cases: tech with unique input/output, etc
    for element in emission_rows:
        if element[2] in techs_emission:
            if element[3] >= START_YEAR:
                key = str(element[2]) + "-" + str(element[3])
                key_out = str(element[2]) + "-" + str(element[3]) + "-" + str(element[4])
                key_input = str(element[2]) + "-" + str(element[3]) + "-" + str(element[1])
                value = float(element[5])
                if element[4] in CO2_OUTPUT and element[0] == "TOT_CO2" or element[0] == "GWP_100":
                    if key not in tech_year_value_map.keys():  # if key is not present yet, add it!
                        tech_year_value_map.update({key: 0.0})
                    if element[2] in tech_in and element[2] in tech_out:
                        value_out = output_split_values_map[key_out]
                        value_in = input_split_values_map[key_input]
                        value = value * value_out * value_in
                        tech_year_value_map.update(
                            {key: tech_year_value_map.get(key) + value})
                    elif element[2] in tech_in and element[2] not in tech_out:
                        value_in = input_split_values_map[key_input]
                        value = value * value_in
                        tech_year_value_map.update(
                            {key: tech_year_value_map.get(key) + value})
                    elif element[2] in tech_out and element[2] not in tech_in:
                        value_out = output_split_values_map[key_out]
                        value = value * value_out
                        tech_year_value_map.update(
                            {key: tech_year_value_map.get(key) + value})
                    else:
                        tech_year_value_map.update(
                            {key: tech_year_value_map.get(key) + value})

    # from a map with tech year value to a map tech year VALID_output and value
    query = "SELECT tech, vintage, output_comm FROM Efficiency"
    cursor.execute(query)
    eff_dummy_rows_tuples = cursor.fetchall()  # fetchall to extract result of last query exectued

    eff_dummy_rows = []
    for row in eff_dummy_rows_tuples:
        eff_dummy_rows.append(list(row))

    eff_dummy = []
    for elem in eff_dummy_rows:
        tech = str(elem[0])
        year = str(elem[1])
        output = str(elem[2])
        if tech in techs_emission:
            eff_dummy.append(tech + "-" + year + "-" + output)

    # delete duplicates
    eff_dummy_new = []
    for elem in eff_dummy:
        tech = elem[0]
        if elem not in eff_dummy_new and tech in techs_emission:
            eff_dummy_new.append(elem)

    tech_year_output_value_map = dict()
    for elem in eff_dummy:
        tech = str(elem.split("-")[0])
        year = int(elem.split("-")[1])
        output = str(elem.split("-")[2])
        if output in VALID_EMISSIONS and year >= START_YEAR:
            key = str(tech) + "-" + str(year) + "-" + str(output)
            key_old = str(tech) + "-" + str(year)  # key old map
            value = float(tech_year_value_map[key_old])
            tech_year_output_value_map.update({key: value})

    # 1/TOS of output under investigation
    for element in tech_year_output_value_map.items():
        key = element[0]
        value = float(element[1])
        tech = key.split("-")[0]
        year = key.split("-")[1]
        output = key.split("-")[2]
        v = -1
        if not output_split_values_map.__contains__(str(tech) + "-" + str(year) + "-" + str(output)):
            v = 1
        else:
            v = float(output_split_values_map.get(str(tech) + "-" + str(year) + "-" + str(output)))
        value = value / float(v)
        tech_year_output_value_map.update({key: value})

    # save it on a csv file
    outFile = csv.writer(open("tech_year_value_em.csv", "w"))
    for key, value in tech_year_output_value_map.items():
        t = key.split("-")[0]
        y = key.split("-")[1]
        o = key.split("-")[2]
        outFile.writerow([t, y, o, value])

    # compare total emission with thresholds of Taxonomy and assign a flag premium (green or brown)

    # create a map valid_emission threshold
    emission_threshold_map = dict()
    for i, emission in enumerate(VALID_EMISSIONS):
        emission_threshold_map[emission] = EMISSION_THRESHOLD[i]

    tech_year_output_map = dict()
    for element in tech_year_output_value_map.items():
        key = element[0]  # key tech year output
        value = element[1]
        key_split = key.split("-")
        tech = key_split[0]
        year = key_split[1]
        output = key_split[2]
        if output in VALID_EMISSIONS:
            if output in CHANGING_THRESHOLD_OUTPUT and int(year) >= 2025:
                # the threshold is 0 => value - threshold = 0
                if value > 0:
                    tech_year_output_map.update({key: "Emission_Penalty"})
                else:
                    tech_year_output_map.update({key: "Emission_Premium"})
            else:
                if value > emission_threshold_map[str(output)]:
                    tech_year_output_map.update({key: "Emission_Penalty"})
                else:
                    tech_year_output_map.update({key: "Emission_Premium"})

    # ---------------------------------------------------------------------------------------------------------------------------------
    # PART 2 : select useful parameters from Efficiency table
    query = "SELECT input_comm, tech, vintage, output_comm, efficiency, eff_notes FROM Efficiency ORDER BY tech"
    cursor.execute(query)
    efficiency_rows_tuples = cursor.fetchall()

    efficiency_rows = []
    for row in efficiency_rows_tuples:
        efficiency_rows.append(list(row))

    # check if there are tech producing output in valid_emission not present in emission map as they do not emit (ex. EV, H2 vehicle, electrolyser)
    # se output = SNK_CO2 non fare niente! xk il premium a DAC l'hai già dato, e le altre tech con SNK_CO2 output sono LINKED e non hanno CostInv

    techFromMap = []
    for element in tech_year_output_map.items():
        key = element[0]
        tech = key.split("-")[0]
        techFromMap.append(tech)

    dummy_chp = []
    for elem in efficiency_rows:
        tech = elem[1]
        if tech == "ELC_CHP_BGS_COG_E":
            dummy_chp.append(elem)

    dummy_map = dict()
    for elem in output_split_values_map.items():
        key = elem[0]
        tech = key.split("-")[0]
        year = key.split("-")[1]
        output = key.split("-")[2]
        value = elem[1]
        if tech == "ELC_CHP_BGS_COG_E":
            key_dummy = str(tech) + "-" + str(year) + "-" + str(output)
            if key_dummy not in dummy_map.keys():
                dummy_map.update({key_dummy: value})

    for element in efficiency_rows:
        input = element[0]
        tech = element[1]
        year = element[2]
        output = element[3]
        key = str(tech) + "-" + str(year) + "-" + str(output)
        if year >= START_YEAR:
            if output in VALID_EMISSIONS and tech not in techFromMap and output != "SNK_CO2" and output not in POWER_OUTPUT:  # EV
                if key not in tech_year_output_map.keys():
                    tech_year_output_map.update({key: "Emission_Premium"})
            if output in GREEN_H2 and tech not in techFromMap and output != "SNK_CO2":  # electrolysers
                if key not in tech_year_output_map.keys():
                    tech_year_output_map.update({key: "Emission_Premium"})
            if output in POWER_OUTPUT and tech in techFromMap:  # power tech emitting
                # check whether it is a CHP plant or not. If so, limit is
                count = 0
                key_dummy = str(tech) + "-" + str(year)
                #for ind in dummy_map.items():
                for ind in output_split_values_map.items():
                    key_out = ind[0]
                    if key_dummy in key_out:
                        count = count + 1
                tot_emission = tech_year_output_value_map.get(key)
                result = check_power(count, tot_emission, input, year, output)
                if result == 1:  # ensure that mix tech (bio+coal) does not have premium
                    tech_year_output_map.update({key: "Emission_Premium"})
                elif result == 0:
                    tech_year_output_map.update({key: "Emission_Penalty"})
            if output in POWER_OUTPUT and tech not in techFromMap:  # assign by default premium for green tech
                if key not in tech_year_output_map.keys():
                    tech_year_output_map.update({key: "Emission_Premium"})

    # delete non Taxonomy mentioned techs: fuel tech (for import) and also RES_CHP and COM_CHP
    outFile = csv.writer(open("trial_taxonomy.csv", "w"))
    for key, value in tech_year_output_map.items():
        t = key.split("-")[0]
        y = key.split("-")[1]
        o = key.split("-")[2]
        outFile.writerow([t, y, o, value])

    # looking for tech whose output is in valid_efficiency
    techs_efficiency = []
    for elem in efficiency_rows:
        if elem[3] in VALID_EFFICIENCY:
            techs_efficiency.append(elem[1])

    # evaluation of electricity consumption: average sum
    tech_year_elc_map = dict()
    for elem in efficiency_rows:
        input = elem[0]
        tech = elem[1]
        year = elem[2]
        output = elem[3]
        value = float(elem[4])
        if input in ELC_TYPES and tech in techs_efficiency and int(year) >= START_YEAR:
            key = str(tech) + "-" + str(year)
            key_out = str(tech) + "-" + str(year) + "-" + str(output)
            if key not in tech_year_elc_map.keys():  # if key is not present yet, add it!
                tech_year_elc_map.update({key: 0.0})
            if tech in tech_out:
                v = float(tech_year_elc_map.get(key))
                if value != v and v != 0.0:  # if efficiency given is for output and not the total one
                    value_out = output_split_values_map[key_out]
                    value = value / value_out
                    tech_year_elc_map.update({key: tech_year_elc_map.get(key) + value})
                else:
                    tech_year_elc_map.update({key: value})
            else:
                tech_year_elc_map.update(
                    {key: tech_year_elc_map.get(key) + value})

    eff_backup = []
    for elem in efficiency_rows:
        input = str(elem[0])
        tech = str(elem[1])
        year = str(elem[2])
        output = str(elem[3])
        if tech in techs_efficiency and input in ELC_TYPES:
            eff_backup.append(tech + "-" + year + "-" + output)

    # delete duplicates
    eff_dummy_again = []
    for elem in eff_backup:
        input = elem[0]
        tech = elem[1]
        if elem not in eff_dummy_again:
            eff_dummy_again.append(elem)

    tech_year_output_eff_map = dict()
    for elem in eff_backup:
        tech = str(elem.split("-")[0])
        year = int(elem.split("-")[1])
        output = str(elem.split("-")[2])
        if year >= START_YEAR:
            key = str(tech) + "-" + str(year) + "-" + str(output)
            key_old = str(tech) + "-" + str(year)  # key old map
            value = float(tech_year_elc_map[key_old])
            tech_year_output_eff_map.update({key: value})

    # TOS of output under investigation
    # looking for HP with multiple output: SC, SH, WH (for them just one value for ELC consumption is needed)
    for element in tech_year_output_eff_map.items():
        key = element[0]
        value = float(element[1])
        tech = key.split("-")[0]
        year = key.split("-")[1]
        output = key.split("-")[2]
        v = -1
        if not output_split_values_map.__contains__(str(tech) + "-" + str(year) + "-" + str(output)) or output in HEAT_PUMP:
            v = 1
        else:
            v = float(output_split_values_map.get(str(tech) + "-" + str(year) + "-" + str(output)))
        value = value * float(v)
        tech_year_output_eff_map.update({key: value})

    # normalize with factors related to RES_SH_SM...
    res_factor_map = dict()
    for i, elem in enumerate(RES_FACTOR_NAME):
        res_factor_map[elem] = RES_FACTOR_VALUE[i]

    for elem in tech_year_output_eff_map.items():
        key = elem[0]
        tech = key.split("-")[0]
        year = key.split("-")[1]
        output = key.split("-")[2]
        value = float(elem[1])
        if output in RES_FACTOR_NAME and tech != "RES_SC_HP_N":  #  RES_SC_HP_N is an exception not to be divided by RES_SC_factor
            value = value/res_factor_map[output]
            tech_year_output_eff_map.update({key: value})

    # save it on a csv file
    outFile = csv.writer(open("tech_year_value_eff.csv", "w"))
    for key, value in tech_year_output_eff_map.items():
        t = key.split("-")[0]
        y = key.split("-")[1]
        o = key.split("-")[2]
        outFile.writerow([t, y, o, value])

    # create a map valid_emission threshold
    efficiency_threshold_map = dict()
    for i, efficiency in enumerate(VALID_EFFICIENCY):
        efficiency_threshold_map[efficiency] = EFFICIENCY_THRESHOLD[i]

    # check for tech using ELC
    for element in tech_year_output_eff_map.items():
        key = element[0]
        value = element[1]
        key_split = key.split("-")
        tech = key_split[0]
        year = key_split[1]
        output = key_split[2]
        if key not in tech_year_output_map.keys():  # if key is not present yet, add it!
            v = "NULL"
            tech_year_output_map.update({key: v})
            if value < efficiency_threshold_map[str(output)]:
                tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Penalty"})
            else:
                tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Premium"})
        else:
            if value < efficiency_threshold_map[str(output)]:
                tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Penalty"})
            else:
                tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Premium"})


    # for tech automatically eligible (es. production of biofuels or WH system fed by solar energy)
    input_control = []
    control = []
    for i, elem in enumerate(efficiency_rows):
        input = elem[0]
        tech = elem[1]
        year = elem[2]
        output = elem[3]
        input_val = str(tech) + "-" + str(year) + "-" + str(input)
        control_val = str(tech) + "-" + str(year)
        if output in OUTPUT_ELIGIBLE and int(year) >= START_YEAR:
            input_control.append(input_val)
            control.append(control_val)

    # delete duplicates from control
    control_dump = []
    for elem in control:
        if elem not in control_dump:
            control_dump.append(elem)

    check_map = dict()
    for i in input_control:
        count = 0
        inp_split = i.split("-")
        tech_i = inp_split[0]
        year_i = inp_split[1]
        input_i = inp_split[2]
        check = str(tech_i) + "-" + str(year_i)
        key = str(tech_i) + "-" + str(year_i) + "-" + str(input_i)
        for elem in control_dump:
            if check in elem:
                count = count + 1
                check_map.update({key: count})

    for element in efficiency_rows:
        input = element[0]
        tech = element[1]
        year = element[2]
        output = element[3]
        key = str(tech) + "-" + str(year) + "-" + str(output)
        key_check = str(tech) + "-" + str(year) + "-" + str(input)
        str_check = "Efficiency_Premium"
        count_check = check_map.get(key_check)
        if year >= START_YEAR:
            if key not in tech_year_output_map.keys() and output in VALID_EFFICIENCY:  # not include all tech in efficiency rows
                v = "NULL"
                tech_year_output_map.update({key: v})
                if output in OUTPUT_ELIGIBLE and input in INPUT_ELIGIBLE and count_check == 1:
                    tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Premium"})
                if output in OUTPUT_ELIGIBLE and input not in INPUT_ELIGIBLE and input not in ELC_TYPES and input != "RES_GEO" and input != "COM_GEO" and output not in UNIQUE_OUTPUT and input not in VALID_EFFICIENCY and str_check not in tech_year_output_map[key]:
                    # penalize RES/COM system not using neither ELC nor GEO but GAS i.e. for SH/SC/WH
                    tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Penalty"})
                    # for ELC_DST only PV will get a premium. Not penalties for the others as they actually falls into ELC and not RES/COM
                if output in ELIGIBLE_DEFAULT and str_check not in tech_year_output_map[key]:
                    tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Premium"})
            else:
                if output in OUTPUT_ELIGIBLE and input in INPUT_ELIGIBLE and count_check == 1:
                    tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Premium"})
                if output in OUTPUT_ELIGIBLE and input not in INPUT_ELIGIBLE and input not in ELC_TYPES and input != "RES_GEO" and input != "COM_GEO" and output not in UNIQUE_OUTPUT and input not in VALID_EFFICIENCY and str_check not in tech_year_output_map[key]:
                    # penalize RES/COM system not using neither ELC nor GEO but GAS i.e. for SH/SC/WH
                    tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Penalty"})
                if output in ELIGIBLE_DEFAULT and str_check not in tech_year_output_map[key]:
                    # avoid multiple eff premium due to multiple input (and so rows in efficiency for the same output)
                    tech_year_output_map.update({key: tech_year_output_map[key] + "-" + "Efficiency_Premium"})

    # filter lines with only "NULL"
    tech_year_final_map = dict()
    for elem in tech_year_output_map.items():
        key_old = elem[0]
        key_split = key_old.split("-")
        tech = key_split[0]
        year = key_split[1]
        output = key_split[2]
        value_old = elem[1]
        key = str(tech) + "-" + str(year) + "-" + str(output)
        if value_old != "NULL":
            tech_year_final_map.update({key: value_old})

    # save the final map on a csv file
    outFile = csv.writer(open("tech_year_output_premium.csv", "w"))
    for key, value in tech_year_final_map.items():
        t = key.split("-")[0]
        y = key.split("-")[1]
        o = key.split("-")[2]
        p = value
        outFile.writerow([t, y, o, p])

    # translate premium/penalty into values
    # FIRST ATTEMPT: premium +26 bp
    premium = - 0.26/100
    penalty = + 0.26/100
    for elem in tech_year_final_map.items():
        key = elem[0]
        value = elem[1]
        if value == "Emission_Premium" or value == "NULL-Efficiency_Premium" or value == "Emission_Premium-Efficiency_Premium":
            value = float(premium)
        elif value == "Emission_Penalty" or value == "NULL-Efficiency_Penalty" or value == "Emission_Penalty-Efficiency_Penalty" or value == "Emission_Penalty-Efficiency_Premium" or value == "Emission_Premium-Efficiency_Penalty":
            value = float(penalty)
        tech_year_final_map.update({key: value})

    # deal with multiple output
    tech_year_taxonomy_map = dict()
    for elem in tech_year_final_map.items():
        key = elem[0]
        div = key.split("-")
        tech = div[0]
        year = div[1]
        output = div[2]
        key_new = str(tech) + "-" + str(year)
        if key_new not in tech_year_taxonomy_map.keys():
            tech_year_taxonomy_map.update({key_new: 0})

    for elem in tech_year_taxonomy_map.items():
        key_new = elem[0]
        count = 0
        for ind in tech_year_final_map.items():
            key = ind[0]
            if key_new in key:
                count = count + 1
        tech_year_taxonomy_map.update({key_new: count})

    for elem in tech_year_taxonomy_map.items():
        key_new = elem[0]
        vect = []
        for ind in tech_year_final_map.items():
            key = ind[0]
            if key_new in key:
                val = float(tech_year_final_map.get(key))
                vect.append(val)
        value = min(vect)  # if one of the output has a penalty, it will prevail
        tech_year_taxonomy_map.update({key_new: value})

    # save the final map on a csv file
    outFile = csv.writer(open("tech_year_taxonomy.csv", "w"))
    for key, value in tech_year_taxonomy_map.items():
        t = key.split("-")[0]
        y = key.split("-")[1]
        p = value
        outFile.writerow([t, y, p])


except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
