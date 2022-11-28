import sqlite3
import csv
from InputOutputSpecialValue import check_value

# Economic parameters for WACC evaluation (Hurdle Rate) (@ 2018)
# HR = WACC = E/E+D*CoE + D/E+D*CoD*(1-CTR) where CoE = RfR + beta_levered*MRP and CoD = EuropeanRfR + CDS

CTR = 24/100
RfR = 2.54/100  # @ 2018
MRP = 9.02/100  # @ 2018
EuropeanRfR = 0.39/100  # @ 2018
CDS = 1.27/100  # @ 2018
COD_after_tax = (1-CTR)*(EuropeanRfR+CDS)

# vector containing output of tech with HR taken from literature: Not issues for input
output_default = ["COM_CK", "COM_WH", "COM_RF", "COM_SC", "COM_SH", "COM_LG",
                  "RES_CK", "RES_WH", "RES_RF_FRZ", "RES_RF_RFG", "RES_SC", "RES_SH_SO", "RES_SH_MO", "RES_SH_SN", "RES_SH_MN",
                  "RES_CW", "RES_CD", "RES_DW", "RES_LG", "RES_INS_C", "RES_INS_MO", "RES_INS_SN", "RES_INS_SO"]

# vector containing output whose input needs to be checked.
# if input not in input_check, HR evaluated by means of economic parameters
output_check = ["TRA_ROA_LCV", "TRA_ROA_MTR", "TRA_ROA_HTR", "TRA_ROA_BUS", "TRA_ROA_CAR", "TRA_AVI_DOM",
                "TRA_AVI_INT", "TRA_NAV_DOM", "TRA_NAV_INT", "TRA_RAIL_FRG", "TRA_RAIL_PSG"]

input_check = ["TRA_ELC", "TRA_H2G", "TRA_H2L", "TRA_AMM"]

# power sector
output_power = ["ELC_CEN", "ELC_DST", "HET"]

# H2 technologies (not CCS)
h2_commodities = ["H2_CT", "H2_CU", "H2_DT", "COM_H2", "RES_H2", "H2_CTE", "H2_CUE", "H2_DTE"]
elc_commodities = ["ELC_CEN", "ELC_DST", "COM_ELC", "COM_HET", "RES_ELC", "RES_HET"]

BASE_YEAR = 2006
try:
    sqliteConnection = sqlite3.connect('db_prova.sqlite')
    cursor = sqliteConnection.cursor()
    print("Database created and Successfully Connected to SQLite")

    # read data of tech having beta, equity and debt ratio
    inFile = csv.reader(open("beta_equity_debt.csv", "r"))
    eco_rows = []
    for row in inFile:
        if len(row) > 0:
            eco_rows.append(row[0])
    output_vector = []
    for elem in eco_rows:
        vect = elem.split(";")
        output_vector.append(vect)

    # create a map containing the name of output with beta, D/D+E, E/D+E
    beta_group = []
    for elem in output_vector:
        beta_group.append(elem[0])

    output_beta_equity_debt_map = dict()
    for elem in eco_rows:
        vect = elem.split(";")
        output = vect[0]
        beta = vect[1]
        equity_ratio = vect[2]
        debt_ratio = vect[3]
        key = output
        value = str(beta) + "-" + str(equity_ratio) + "-" + str(debt_ratio)
        if key not in output_beta_equity_debt_map.keys():  # if key is not present yet, add it!
            output_beta_equity_debt_map.update({key: value})


    # read data of tech having discount rate defined in literature
    inFile = csv.reader(open("hurdle_rate_default.csv", "r"))
    hr_rows = []
    for row in inFile:
        if len(row) > 0:
            hr_rows.append(row[0])

    # create a map containing the name of output with HR by default
    hr_default_map = dict()
    for elem in hr_rows:
        vect = elem.split(";")
        output = vect[0]
        hr = vect[1]
        key = str(output)
        value = float(hr)/100
        if key not in hr_default_map.keys():  # if key is not present yet, add it!
            hr_default_map.update({key: value})

    # take from DB input-output-tech
    query = "SELECT input_comm, tech, vintage, output_comm FROM Efficiency ORDER BY tech"
    cursor.execute(query)
    tech_rows_tuples = cursor.fetchall()

    tech_rows = []
    for row in tech_rows_tuples:
        tech_rows.append(list(row))

    # take from DB list of tech having CCS
    query = "SELECT primary_tech from LinkedTechs"
    cursor.execute(query)
    linked_tech_rows_tuples = cursor.fetchall()

    linked_tech_rows = []
    for row in linked_tech_rows_tuples:
        linked_tech_rows.append(row[0])


    # for tech having HR by formula and by literature (according with the type of input) we must check whether they have
    # more than one input and whether it is contained in input_check
    input_control = []
    control = []
    for i, elem in enumerate(tech_rows):
        input = elem[0]
        tech = elem[1]
        year = elem[2]
        output = elem[3]
        input_val = str(tech) + "-" + str(year) + "-" + str(input)
        control_val = str(tech) + "-" + str(year)
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

    hurdle_value_map = dict()
    for elem in tech_rows:
        input = elem[0]
        tech = elem[1]
        year = elem[2]
        output = elem[3]
        if int(year) > BASE_YEAR:
            key = str(tech) + "-" + str(year) + "-" + str(output) + "-" + str(input)
            key_check = str(tech) + "-" + str(year) + "-" + str(input)
            count_check = check_map.get(key_check)
            # case 1: tech with beta, E/D+E, D/D+E by literature

            if output in beta_group and str(tech) not in linked_tech_rows:
                key_eco = str(output)
                eco_parameters = output_beta_equity_debt_map.get(key_eco)
                div = eco_parameters.split("-")
                beta = float(div[0])
                equity_ratio = float(div[1])/100
                debt_ratio = float(div[2])/100
                if input not in input_check:  # just one input not in input_check
                    COE = RfR + beta * MRP
                    value = COE * equity_ratio + debt_ratio * COD_after_tax
                if input in input_check:  # just one input and in input_check
                    value = check_value(tech, output, input)
                hurdle_value_map.update({key: value})
            # case 2: industrial tech with CCS (their HR should be higher)
            if output in beta_group and str(tech) in linked_tech_rows:
                value = 15/100
                hurdle_value_map.update({key: value})
            # case 3: tech with HR by literature
            if output in output_default:
                key_hr = str(output)
                value = hr_default_map.get(key_hr)
                hurdle_value_map.update({key: value})
            # case 4: tech in power sector, HR by literature depending on the source
            if output in output_power:
                value = check_value(tech, output, input)
                hurdle_value_map.update({key: value})
            # case 5: H2 technologies (not CCUS). 3 sub-cases: production, use and storage of h2_commodities
            if (output in h2_commodities and input in elc_commodities and tech not in linked_tech_rows) or (input in h2_commodities and output in elc_commodities) or (output in h2_commodities and input in h2_commodities):
                value = 8/100
                hurdle_value_map.update({key: value})
            # case 6: CO2 capture and storage tech
            if (output == "SNK_CO2" and input in output_power) or (output == "DMY_OUT" and input == "SNK_CO2"):
                value = 10/100
                hurdle_value_map.update({key: value})

    tech_year_output_hurdle_map = dict()
    # deal with multiple input (es. hybrid cars or elc plants)
    for elem in hurdle_value_map.items():
        key = elem[0]
        div = key.split("-")
        tech = div[0]
        year = div[1]
        output = div[2]
        input = div[3]
        key_new = str(tech) + "-" + str(year) + "-" + str(output)
        if key_new not in tech_year_output_hurdle_map.keys():
            tech_year_output_hurdle_map.update({key_new: 0})

    for elem in tech_year_output_hurdle_map.items():
        key_new = elem[0]
        count = 0
        for ind in hurdle_value_map.items():
            key = ind[0]
            if key_new in key:
                count = count + 1

        tech_year_output_hurdle_map.update({key_new: count})



except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)